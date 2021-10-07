"""Wrapper around the FastApiCache-2 library"""
from fastapi_cache.decorator import cache

from ccdh.config import get_settings


# Note: args and kwargs left here because they are used by...
# ...`fastapi_cache.decorator.cache`
# noinspection PyUnusedLocal
def nocache(*args, **kwargs):
    """Wrapper func"""
    def decorator(func):
        """Decorator"""
        return func
    return decorator


if get_settings().environment_name == 'production':
    cache = cache
else:
    cache = nocache
