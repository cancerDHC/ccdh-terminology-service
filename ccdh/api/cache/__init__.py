"""Wrapper around the FastApiCache-2 library"""
from fastapi_cache.decorator import cache

from ccdh.config import get_settings


def nocache():
    def decorator(func):
        return func
    return decorator


if get_settings().environment_name == 'production':
    cache = cache
else:
    cache = nocache
