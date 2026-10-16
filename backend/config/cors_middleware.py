from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Magia pura: Si el navegador envía la petición fantasma OPTIONS, 
        # le respondemos un OK (200) vacío inmediatamente para que nos deje pasar.
        if request.method == "OPTIONS":
            return HttpResponse()

    def process_response(self, request, response):
        allowed_origins = ['http://127.0.0.1:5500', 'http://localhost:5500']
        origin = request.headers.get('Origin')
        
        if origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
        else:
            response["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
            
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-Idempotency-Key, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response