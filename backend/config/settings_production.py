"""Configuración AWS sin dependencias en la instalación privada de un integrante."""
import os

os.environ.setdefault('SGR_LOAD_DOTENV', 'False')
from .settings import *
from django.core.exceptions import ImproperlyConfigured


def required(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise ImproperlyConfigured(f'Falta configurar {name} en el servidor.')
    return value


DEBUG = False
SECRET_KEY = required('SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('fallback'):
    raise ImproperlyConfigured('SECRET_KEY debe ser exclusiva y aleatoria.')
ALLOWED_HOSTS = [v.strip() for v in required('ALLOWED_HOSTS').split(',') if v.strip()]
if not ALLOWED_HOSTS or any('*' in v or '://' in v or '/' in v for v in ALLOWED_HOSTS):
    raise ImproperlyConfigured('ALLOWED_HOSTS requiere nombres o IP explícitos.')
CSRF_TRUSTED_ORIGINS = [v.strip() for v in required('CSRF_TRUSTED_ORIGINS').split(',') if v.strip()]
if not CSRF_TRUSTED_ORIGINS or any(not v.startswith('https://') or '*' in v for v in CSRF_TRUSTED_ORIGINS):
    raise ImproperlyConfigured('CSRF_TRUSTED_ORIGINS requiere orígenes HTTPS explícitos.')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# Gunicorn solo escucha loopback; Nginx sobrescribe esta cabecera.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = 'DENY'
for key in ['NAME', 'HOST', 'USER', 'PASSWORD']:
    DATABASES['default'][key] = required('DB_' + key)
DATABASES['default']['PORT'] = os.environ.get('DB_PORT', '3306')
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'charset': 'utf8mb4',
    'ssl': {'ca': required('RDS_CA_PATH')},
    'ssl_mode': 'VERIFY_IDENTITY',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
}
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': required('AWS_STORAGE_BUCKET_NAME'),
            'region_name': required('AWS_REGION'),
            'default_acl': None,
            'querystring_auth': True,
            'querystring_expire': 300,
            'file_overwrite': False,
            'location': '',
            'object_parameters': {'ServerSideEncryption': 'AES256'},
        },
    },
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
STATIC_URL = '/static/'
LOGGING = {
    'version': 1, 'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
