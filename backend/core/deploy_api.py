"""Comprobaciones mínimas del despliegue, sin publicar configuración privada."""
import os
import re
from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def version(request):
    value = os.environ.get('GIT_SHA', '')
    release = value if re.fullmatch(r'[0-9a-f]{40}', value) else 'unknown'
    response = JsonResponse({'service': 'SGR', 'version': release})
    response['Cache-Control'] = 'no-store'
    return response


def probe_database():
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        return cursor.fetchone()


@require_safe
def health(request):
    try:
        probe_database()
    except DatabaseError:
        return JsonResponse({'status': 'unavailable'}, status=503)
    response = JsonResponse({'status': 'ok'})
    response['Cache-Control'] = 'no-store'
    return response
