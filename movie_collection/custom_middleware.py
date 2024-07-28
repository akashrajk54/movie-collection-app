import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

from accounts_engine.utils import success_false_response
from accounts_engine.models import InvalidatedToken

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


class TokenInvalidatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else auth_header
            if token in InvalidatedToken.objects.values_list("token", flat=True):
                logger_info.info(f"Token: {token} is invalid.")
                response_data = success_false_response(message="Please login.")
                response = JsonResponse(response_data, status=401)
                return response

        except Exception:
            pass

        response = self.get_response(request)
        return response


class RequestCounterMiddleware(MiddlewareMixin):
    REQUEST_COUNT_CACHE_KEY = 'request_count'

    def process_request(self, request):
        try:
            # Check if the request count key exists
            if cache.get(self.REQUEST_COUNT_CACHE_KEY) is not None:
                # Increment the request count if the key exists
                cache.incr(self.REQUEST_COUNT_CACHE_KEY)
            else:
                # Set the request count to 1 if the key does not exist
                cache.set(self.REQUEST_COUNT_CACHE_KEY, 1)
        except Exception as e:
            # Log the exception or handle as needed
            print(f"Error incrementing request count: {e}")
