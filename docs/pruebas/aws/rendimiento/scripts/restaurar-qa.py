import json,os,shlex,subprocess,time,re
from pathlib import Path
from datetime import datetime,timezone
private=json.loads(Path('/home/ubuntu/aws-migration-private.json').read_text());env={}
for line in Path('/etc/sgr/sgr.env').read_text().splitlines():
 if line.strip() and not line.lstrip().startswith('#'):
  k,v=line.split('=',1);parts=shlex.split(v);env[k]=parts[0] if parts else ''
assert env['DB_NAME']=='sgr_prueba' and env['DB_HOST'].endswith('.rds.amazonaws.com')
conf=Path('/etc/sgr/restore-qa.cnf');db='sgr_restore_qa_'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S');assert re.fullmatch('sgr_restore_qa_[0-9]+',db)
def esc(v):return '"'+str(v).replace('\\','\\\\').replace('"','\\"')+'"'
conf.write_text('[client]\n'+''.join(k+'='+esc(v)+'\n' for k,v in [('host',env['DB_HOST']),('port',env['DB_PORT']),('user',private['user']),('password',private['password']),('ssl-ca',env['RDS_CA_PATH']),('ssl-mode','VERIFY_IDENTITY')]));conf.chmod(0o600)
base=['mysql','--defaults-extra-file='+str(conf),'--batch','--skip-column-names'];made=False;start=time.monotonic();report={'database_temporal':db,'inicio_utc':datetime.now(timezone.utc).isoformat()};dump=Path('/srv/sgr/backups')/(db+'.sql')
def sql(q):
 r=subprocess.run(base+['-e',q],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode:raise RuntimeError('Falló operación SQL de ensayo aislado.')
 return r.stdout.decode().strip()
try:
 subprocess.run(['systemctl','stop','sgr'],check=True)
 names=sql("SELECT table_name FROM information_schema.tables WHERE table_schema='sgr_prueba' AND table_type='BASE TABLE'").splitlines();assert all(re.fullmatch('[A-Za-z0-9_]+',t) for t in names)
 before={t:{'count':int(sql('SELECT COUNT(*) FROM sgr_prueba.`'+t+'`')),'checksum':sql('CHECKSUM TABLE sgr_prueba.`'+t+'` EXTENDED').split('\t')[-1]} for t in names}
 fd=os.open(dump,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as out:
  r=subprocess.run(['mysqldump','--defaults-extra-file='+str(conf),'--single-transaction','--no-tablespaces','--set-gtid-purged=OFF','--column-statistics=0','sgr_prueba'],stdout=out,stderr=subprocess.PIPE)
  if r.returncode:raise RuntimeError('No se pudo respaldar; no se restauró nada.')
 assert dump.stat().st_size>1000
 assert not re.search(r'^(?:USE |CREATE DATABASE)',dump.read_text(),re.M)
 sql('CREATE DATABASE `'+db+'` CHARACTER SET utf8mb4');made=True
 restore_start=time.monotonic()
 with dump.open('rb') as inp:
  r=subprocess.run(base+[db],stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if r.returncode:raise RuntimeError('Falló restauración en esquema QA aislado.')
 report['restauracion_s']=round(time.monotonic()-restore_start,3)
 after={t:{'count':int(sql('SELECT COUNT(*) FROM `'+db+'`.`'+t+'`')),'checksum':sql('CHECKSUM TABLE `'+db+'`.`'+t+'` EXTENDED').split('\t')[-1]} for t in names}
 report.update(tablas=len(names),filas=sum(v['count'] for v in before.values()),conteos_y_checksums_iguales=before==after,checksums_disponibles=all(v['checksum']!='NULL' for v in before.values()),comparacion={t:{'filas':before[t]['count'],'coincide':before[t]==after[t]} for t in names},backup_bytes=dump.stat().st_size)
 if before!=after:raise RuntimeError('Diferencia de integridad entre respaldo y clon QA.')
finally:
 try:
  if made:
   sql('DROP DATABASE `'+db+'`');report['esquema_temporal_eliminado']=True
 finally:
  subprocess.run(['systemctl','start','sgr'],check=True)
  conf.unlink(missing_ok=True);Path('/home/ubuntu/aws-migration-private.json').unlink(missing_ok=True)
  report['ventana_operacion_s']=round(time.monotonic()-start,3)
  p=Path('/home/ubuntu/restore-resultado.json');p.write_text(json.dumps(report,indent=2));p.chmod(0o644)
print(json.dumps({k:v for k,v in report.items() if k!='comparacion'}))
