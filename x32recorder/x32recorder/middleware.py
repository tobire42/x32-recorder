"""
Middleware to redirect HTTPS requests to HTTP
"""
from django.shortcuts import redirect


class HttpRedirectMiddleware:
    """
    Redirects all HTTPS requests to HTTP.
    Useful for development environments or local networks where HTTPS is not needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request is HTTPS
        if request.is_secure():
            # Build the HTTP URL
            url = request.build_absolute_uri()
            secure_url = url.replace("https://", "http://", 1)
            return redirect(secure_url, permanent=True)
        
        response = self.get_response(request)
        return response
