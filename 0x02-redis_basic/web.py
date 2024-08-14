#!/usr/bin/env python3

"""Web Module"""

import redis
import requests
from functools import wraps
from typing import Callable


r = redis.Redis()
"""Redis instance"""


def data_cacher(method: Callable) -> Callable:
    """Decorator that caches the result of a method"""

    @wraps(method)
    def invoker(url) -> str:
        """Wrapper function"""
        r.incr(f"count:{url}")
        result = r.get(f"result:{url}")
        if result:
            return result.decode("utf-8")
        result = method(url)
        r.set(f"count:{url}", 0)
        r.setex(f"result:{url}", 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    """Get the content of a web page"""
    return requests.get(url).text
