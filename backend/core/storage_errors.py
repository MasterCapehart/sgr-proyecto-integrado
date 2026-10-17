"""Clasifica errores esperados sin ocultar errores de programación."""
def storage_error(exc):
    if isinstance(exc, FileNotFoundError):
        return 404, 'El archivo no está disponible.'
    try:
        from botocore.exceptions import ClientError, BotoCoreError
    except ImportError:
        return None
    if isinstance(exc, ClientError):
        code = str(exc.response.get('Error', {}).get('Code', ''))
        if code in {'NoSuchKey', 'NotFound', '404'}:
            return 404, 'El archivo no está disponible.'
        return 503, 'El almacenamiento no está disponible. Intenta nuevamente.'
    if isinstance(exc, BotoCoreError):
        return 503, 'El almacenamiento no está disponible. Intenta nuevamente.'
    return None
