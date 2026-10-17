#!/usr/bin/env python3
"""Crear recursos propios de AWS-TEST. Requiere --apply y perfil autorizado.
El estado y las contraseñas se guardan fuera de Git. No modifica recursos ajenos.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import secrets
import urllib.request
import uuid

import boto3
from botocore.config import Config

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--profile', default='sgr-aws')
parser.add_argument('--region', default='us-east-1')
parser.add_argument('--state', default='.integracion/aws-deploy/state.json')
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()
if not args.apply:
    parser.error('Esta operación crea recursos con costo. Usar --apply tras revisar el plan.')
state_path = Path(args.state).resolve()
state_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
state_path.parent.chmod(0o700)
if state_path.exists():
    state = json.loads(state_path.read_text())
    if state.get('region') != args.region:
        parser.error('No se permite cambiar región de un estado existente.')
else:
    state = {'region': args.region, 'deployment': uuid.uuid4().hex[:12]}


def save():
    tmp = state_path.with_suffix('.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(state, stream, indent=2)
    tmp.replace(state_path)


session = boto3.Session(profile_name=args.profile, region_name=args.region)
config = Config(retries={'max_attempts': 4, 'mode': 'standard'}, connect_timeout=10, read_timeout=30)
ec2 = session.client('ec2', config=config)
rds = session.client('rds', config=config)
s3 = session.client('s3', config=config)
identity = session.client('sts', config=config).get_caller_identity()
if state.get('account') and state['account'] != identity['Account']:
    raise SystemExit('El estado pertenece a otra cuenta. No se continúa.')
state['account'] = identity['Account']
save()
tags = [{'Key':'Proyecto','Value':'SGR'},{'Key':'Entorno','Value':'AWS-TEST'},
        {'Key':'SGRDeployment','Value':state['deployment']}]


def tag(kind, name):
    return [{'ResourceType':kind,'Tags':tags + [{'Key':'Name','Value':name}]}]


zones = sorted(z['ZoneName'] for z in ec2.describe_availability_zones()['AvailabilityZones']
               if z['State'] == 'available' and z.get('ZoneType','availability-zone') == 'availability-zone')
if len(zones) < 2:
    raise SystemExit('Se requieren dos zonas disponibles para RDS.')
if 'vpc' not in state:
    state['vpc'] = ec2.create_vpc(CidrBlock='10.20.0.0/16', TagSpecifications=tag('vpc','sgr-test'))['Vpc']['VpcId']; save()
    ec2.modify_vpc_attribute(VpcId=state['vpc'], EnableDnsSupport={'Value':True})
    ec2.modify_vpc_attribute(VpcId=state['vpc'], EnableDnsHostnames={'Value':True})
if 'public_subnet' not in state:
    state['public_subnet'] = ec2.create_subnet(VpcId=state['vpc'], CidrBlock='10.20.1.0/24', AvailabilityZone=zones[0], TagSpecifications=tag('subnet','sgr-publica'))['Subnet']['SubnetId'];save()
    ec2.modify_subnet_attribute(SubnetId=state['public_subnet'], MapPublicIpOnLaunch={'Value':True})
for i in [0,1]:
    key=f'private_subnet_{i}'
    if key not in state:
        state[key]=ec2.create_subnet(VpcId=state['vpc'], CidrBlock=f'10.20.{11+i}.0/24', AvailabilityZone=zones[i],TagSpecifications=tag('subnet',f'sgr-privada-{i}'))['Subnet']['SubnetId'];save()
if 'igw' not in state:
    state['igw']=ec2.create_internet_gateway(TagSpecifications=tag('internet-gateway','sgr-igw'))['InternetGateway']['InternetGatewayId'];save()
    ec2.attach_internet_gateway(VpcId=state['vpc'],InternetGatewayId=state['igw'])
if 'public_route_table' not in state:
    state['public_route_table']=ec2.create_route_table(VpcId=state['vpc'],TagSpecifications=tag('route-table','sgr-publica'))['RouteTable']['RouteTableId'];save()
    ec2.create_route(RouteTableId=state['public_route_table'],DestinationCidrBlock='0.0.0.0/0',GatewayId=state['igw'])
    ec2.associate_route_table(RouteTableId=state['public_route_table'],SubnetId=state['public_subnet'])
if 'web_sg' not in state:
    state['web_sg']=ec2.create_security_group(GroupName='sgr-web-'+state['deployment'],Description='SGR HTTPS and restricted administration',VpcId=state['vpc'],TagSpecifications=tag('security-group','sgr-web'))['GroupId'];save()
    with urllib.request.urlopen('https://checkip.amazonaws.com',timeout=15) as response:
        address=str(ipaddress.IPv4Address(response.read().decode().strip()))
    ec2.authorize_security_group_ingress(GroupId=state['web_sg'],IpPermissions=[
        {'IpProtocol':'tcp','FromPort':22,'ToPort':22,'IpRanges':[{'CidrIp':address+'/32','Description':'Administrador local'}]},
        {'IpProtocol':'tcp','FromPort':80,'ToPort':80,'IpRanges':[{'CidrIp':'0.0.0.0/0','Description':'ACME y redireccion HTTPS'}]},
        {'IpProtocol':'tcp','FromPort':443,'ToPort':443,'IpRanges':[{'CidrIp':'0.0.0.0/0','Description':'SGR HTTPS'}]},
    ])
if 'db_sg' not in state:
    state['db_sg']=ec2.create_security_group(GroupName='sgr-db-'+state['deployment'],Description='SGR MySQL only from application SG',VpcId=state['vpc'],TagSpecifications=tag('security-group','sgr-db'))['GroupId'];save()
    ec2.authorize_security_group_ingress(GroupId=state['db_sg'],IpPermissions=[{'IpProtocol':'tcp','FromPort':3306,'ToPort':3306,'UserIdGroupPairs':[{'GroupId':state['web_sg']}]}])
if 'bucket' not in state:
    bucket='sgr-evidencias-'+state['deployment']
    options={'Bucket':bucket}
    if args.region != 'us-east-1': options['CreateBucketConfiguration']={'LocationConstraint':args.region}
    s3.create_bucket(**options);state['bucket']=bucket;save()
    s3.put_public_access_block(Bucket=bucket,PublicAccessBlockConfiguration={'BlockPublicAcls':True,'IgnorePublicAcls':True,'BlockPublicPolicy':True,'RestrictPublicBuckets':True})
    s3.put_bucket_encryption(Bucket=bucket,ServerSideEncryptionConfiguration={'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]})
    s3.put_bucket_versioning(Bucket=bucket,VersioningConfiguration={'Status':'Enabled'})
    s3.put_bucket_tagging(Bucket=bucket,Tagging={'TagSet':tags})
if 'db_subnet_group' not in state:
    name='sgr-subnets-'+state['deployment']
    rds.create_db_subnet_group(DBSubnetGroupName=name,DBSubnetGroupDescription='SGR private database subnets',SubnetIds=[state['private_subnet_0'],state['private_subnet_1']],Tags=tags)
    state['db_subnet_group']=name;save()
if 'db_instance' not in state:
    name='sgr-mysql-'+state['deployment']
    versions=rds.describe_db_engine_versions(Engine='mysql',EngineVersion='8.4',DefaultOnly=True)['DBEngineVersions']
    if not versions: versions=rds.describe_db_engine_versions(Engine='mysql',DefaultOnly=True)['DBEngineVersions']
    engine=versions[0]['EngineVersion']
    state['db_master_user']='sgr_deploy';state['db_master_password']=secrets.token_urlsafe(32);state['db_app_password']=secrets.token_urlsafe(32);save()
    rds.create_db_instance(DBInstanceIdentifier=name,DBInstanceClass='db.t3.micro',Engine='mysql',EngineVersion=engine,MasterUsername=state['db_master_user'],MasterUserPassword=state['db_master_password'],DBName='sgr_prueba',AllocatedStorage=20,StorageType='gp3',StorageEncrypted=True,PubliclyAccessible=False,MultiAZ=False,VpcSecurityGroupIds=[state['db_sg']],DBSubnetGroupName=state['db_subnet_group'],BackupRetentionPeriod=7,DeletionProtection=True,AutoMinorVersionUpgrade=True,Tags=tags)
    state['db_instance']=name;state['db_engine']=engine;save()
if 'key_pair' not in state:
    name='sgr-key-'+state['deployment']
    key=ec2.create_key_pair(KeyName=name,KeyType='ed25519',TagSpecifications=tag('key-pair','sgr-key'))
    fd=os.open(state_path.parent/'ec2-key.pem',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w')as stream:stream.write(key['KeyMaterial'])
    state['key_pair']=name;save()
if 'instance' not in state:
    images=ec2.describe_images(Owners=['099720109477'],Filters=[{'Name':'name','Values':['ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*']},{'Name':'state','Values':['available']}])['Images']
    image=sorted(images,key=lambda item:item['CreationDate'])[-1]['ImageId']
    userdata='''#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-dev build-essential default-libmysqlclient-dev pkg-config nginx mysql-client ca-certificates curl rsync snapd
useradd --system --create-home --home-dir /srv/sgr --shell /usr/sbin/nologin sgr
usermod -aG sgr www-data
chmod 750 /srv/sgr
install -d -m 750 -o root -g sgr /etc/sgr
install -d -m 755 /var/lib/letsencrypt/.well-known/acme-challenge
curl --fail --location https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /etc/sgr/rds-ca.pem
chmod 644 /etc/sgr/rds-ca.pem
'''
    instance=ec2.run_instances(ImageId=image,InstanceType='t3.small',MinCount=1,MaxCount=1,KeyName=state['key_pair'],IamInstanceProfile={'Name':'LabInstanceProfile'},NetworkInterfaces=[{'DeviceIndex':0,'SubnetId':state['public_subnet'],'Groups':[state['web_sg']],'AssociatePublicIpAddress':True}],MetadataOptions={'HttpTokens':'required','HttpEndpoint':'enabled'},BlockDeviceMappings=[{'DeviceName':'/dev/sda1','Ebs':{'VolumeSize':20,'VolumeType':'gp3','Encrypted':True,'DeleteOnTermination':True}}],TagSpecifications=tag('instance','sgr-web-test'),UserData=userdata)['Instances'][0]
    state['instance']=instance['InstanceId'];save()
if 'elastic_ip_allocation' not in state:
    allocation=ec2.allocate_address(Domain='vpc',TagSpecifications=tag('elastic-ip','sgr-ip'))
    state['elastic_ip_allocation']=allocation['AllocationId'];state['public_ip']=allocation['PublicIp'];save()
    ec2.get_waiter('instance_running').wait(InstanceIds=[state['instance']],WaiterConfig={'Delay':10,'MaxAttempts':12})
    ec2.associate_address(InstanceId=state['instance'],AllocationId=state['elastic_ip_allocation'])
print(json.dumps({'estado':'Recursos solicitados; falta configuración y verificación','instance':state['instance'],'public_ip':state['public_ip'],'database':state['db_instance'],'bucket':state['bucket']},indent=2))
