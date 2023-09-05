from django.conf import settings
from django.urls import resolve

class ValidateTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [f"api_{version}_{url_name}" for version in settings.API_VERSIONS for url_name in
                            ["login", "register"]]

    def __call__(self, request):
        response = self.get_response(request)
        return response