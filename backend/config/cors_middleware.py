from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse()
            # Forzamos las cabeceras desde el preflight para asegurar el pase
            origin = request.headers.get('Origin')
            if origin in ['http://127.0.0.1:5500', 'http://localhost:5500']:
                response["Access-Control-Allow-Origin"] = origin
            else:
                response["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
                
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Idempotency-Key, X-CSRFToken"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

    def process_response(self, request, response):
        origin = request.headers.get('Origin')
        
        # Eliminamos cualquier comodín '*' que Django haya puesto por defecto
        if "Access-Control-Allow-Origin" in response:
            del response["Access-Control-Allow-Origin"]
            
        if origin in ['http://127.0.0.1:5500', 'http://localhost:5500']:
            response["Access-Control-Allow-Origin"] = origin
        else:
            response["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
            
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Idempotency-Key, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response