import time

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        print(f"[LOG] Method: {request.method} | URL: {request.path} | Execution Time: {duration:.4f}s")
        
        return response
