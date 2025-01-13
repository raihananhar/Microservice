from django.core.cache import cache
from rest_framework.exceptions import Throttled
from django.utils import timezone

def rate_limit(key, limit, period):
    now = timezone.now()
    request_count = cache.get(key, 0)
    
    if request_count >= limit:
        raise Throttled(detail=f"Rate limit exceeded. Try again in {period} seconds.")
    
    cache.set(key, request_count + 1, period)