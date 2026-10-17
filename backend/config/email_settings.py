"""Configuración de correo; no abre conexiones ni envía mensajes al importar."""
import os
from email.utils import parseaddr

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email


def email_configuration():
    mode = os.getenv('SGR_EMAIL_MODE', 'local').strip().lower()
    if mode not in {'local', 'smtp'}:
        raise ImproperlyConfigured('SGR_EMAIL_MODE debe ser local o smtp.')
    if mode == 'local':
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
            'DEFAULT_FROM_EMAIL': 'SGR <no-responder@sgr.local>',
        }

    def boolean(name, default):
        value = os.getenv(name, default).strip().lower()
        if value not in {'true', 'false'}:
            raise ImproperlyConfigured(f'{name} debe ser True o False.')
        return value == 'true'

    tls = boolean('EMAIL_USE_TLS', 'True')
    ssl = boolean('EMAIL_USE_SSL', 'False')
    if tls == ssl:
        raise ImproperlyConfigured('SMTP requiere TLS o SSL, activando solo uno.')
    host = os.getenv('EMAIL_HOST', '').strip()
    user = os.getenv('EMAIL_HOST_USER', '').strip()
    password = os.getenv('EMAIL_HOST_PASSWORD', '')
    sender = os.getenv('DEFAULT_FROM_EMAIL', '').strip() or user
    if not host or not sender:
        raise ImproperlyConfigured('Configura EMAIL_HOST y DEFAULT_FROM_EMAIL para SMTP.')
    if bool(user) != bool(password):
        raise ImproperlyConfigured('Configura conjuntamente usuario y contraseña SMTP.')
    try:
        if '\r' in sender or '\n' in sender:
            raise ValidationError('Remitente inválido.')
        validate_email(parseaddr(sender)[1])
        port = int(os.getenv('EMAIL_PORT', '465' if ssl else '587'))
        timeout = int(os.getenv('EMAIL_TIMEOUT', '10'))
        if not 1 <= port <= 65535 or not 1 <= timeout <= 30:
            raise ValueError
    except (ValueError, ValidationError):
        raise ImproperlyConfigured('Revisa el remitente, puerto y tiempo de espera SMTP.') from None
    return {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': host,
        'EMAIL_PORT': port,
        'EMAIL_HOST_USER': user,
        'EMAIL_HOST_PASSWORD': password,
        'EMAIL_USE_TLS': tls,
        'EMAIL_USE_SSL': ssl,
        'EMAIL_TIMEOUT': timeout,
        'DEFAULT_FROM_EMAIL': sender,
    }
