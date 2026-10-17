"""Controles de configuración y contratos del despliegue, sin consumir AWS."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import importlib.util
from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]

class ProductionConfiguration(SimpleTestCase):
    def load_settings(self, **changes):
        env = os.environ.copy()
        env.update(SECRET_KEY='q'*64, ALLOWED_HOSTS='192.0.2.10',
                   CSRF_TRUSTED_ORIGINS='https://192.0.2.10',
                   DB_HOST='database.example.test', DB_NAME='sgr_prueba',
                   DB_USER='sgr_app', DB_PASSWORD='ficticia-no-real', DB_PORT='3306',
                   AWS_STORAGE_BUCKET_NAME='bucket-ejemplo-test', AWS_REGION='us-east-1',
                   RDS_CA_PATH='/tmp/ca-ejemplo.pem', SGR_EMAIL_MODE='local',
                   SGR_LOAD_DOTENV='False')
        for key,value in changes.items():
            if value is None: env.pop(key, None)
            else: env[key] = value
        script = '''import json
from config import settings_production as s
print(json.dumps({'debug':s.DEBUG,'secure':s.SESSION_COOKIE_SECURE,
'csrf':s.CSRF_COOKIE_SECURE,'redirect':s.SECURE_SSL_REDIRECT,
'hosts':s.ALLOWED_HOSTS,'storage':s.STORAGES['default'],
'options':s.DATABASES['default']['OPTIONS']}))'''
        return subprocess.run([sys.executable,'-c',script],cwd=ROOT,env=env,
                              text=True,capture_output=True)
    def test_production_forces_https_private_storage_and_verified_database(self):
        p=self.load_settings(DEBUG='True')
        self.assertEqual(p.returncode,0,p.stderr)
        value=json.loads(p.stdout)
        self.assertFalse(value['debug'])
        self.assertTrue(value['secure'] and value['csrf'] and value['redirect'])
        self.assertEqual(value['options']['ssl_mode'],'VERIFY_IDENTITY')
        self.assertIsNone(value['storage']['OPTIONS']['default_acl'])
        self.assertEqual(value['storage']['OPTIONS']['location'],'')
        self.assertNotIn('access_key',value['storage']['OPTIONS'])
    def test_missing_secret_rejected_without_reading_local_env(self):
        p=self.load_settings(SECRET_KEY=None)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SECRET_KEY',p.stderr)
    def test_wildcard_host_rejected(self):
        self.assertNotEqual(self.load_settings(ALLOWED_HOSTS='*').returncode,0)

class StorageFailures(SimpleTestCase):
    @unittest.skipUnless(importlib.util.find_spec("botocore"), "Instalar requirements-production.txt para verificar S3")
    def test_missing_and_unavailable_are_distinguished(self):
        from core.storage_errors import storage_error
        from botocore.exceptions import ClientError, EndpointConnectionError
        missing=ClientError({'Error':{'Code':'NoSuchKey'}},'GetObject')
        denied=ClientError({'Error':{'Code':'AccessDenied'}},'GetObject')
        self.assertEqual(storage_error(missing)[0],404)
        self.assertEqual(storage_error(denied)[0],503)
        self.assertEqual(storage_error(EndpointConnectionError(endpoint_url='https://example.test'))[0],503)
        self.assertIsNone(storage_error(ValueError('programming error')))

class DeploymentEndpoints(SimpleTestCase):
    def test_version_exposes_only_release_identifier(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {'GIT_SHA':'a'*40, 'SECRET_KEY':'private-not-for-response'}):
            response=self.client.get('/api/version/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),{'service':'SGR','version':'a'*40})
        self.assertNotIn('private-not-for-response',response.content.decode())
    def test_database_health_failure_is_generic(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        with patch('core.deploy_api.probe_database',side_effect=DatabaseError('private-host')):
            response=self.client.get('/api/health/')
        self.assertEqual(response.status_code,503)
        self.assertNotIn('private-host',response.content.decode())
