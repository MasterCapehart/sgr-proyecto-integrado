from django.http import HttpResponse

class CorsMiddleware:
    """
    Middleware ligero para permitir peticiones AJAX/fetch desde el frontend
    con soporte explícito para credenciales de seguridad (Cookies y CSRF Token).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse()
        else:
            response = self.get_response(request)

        # 1. Identificar desde dónde nos están llamando
        origin = request.headers.get('Origin')
        
        # Orígenes autorizados (tu Live Server de Visual Studio Code)
        allowed_origins = ["http://127.0.0.1:5500", "http://localhost:5500"]

        # 2. Reemplazar el "*" por el origen exacto si está en la lista blanca
        if origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
        else:
            # Fallback por defecto
            response["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"

        # 3. Habilitar explícitamente el uso de credenciales seguras
        response["Access-Control-Allow-Credentials"] = "true"
        
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        
        # 4. Incluimos X-CSRFToken en los headers permitidos
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Idempotency-Key, X-CSRFToken"
        
        return response