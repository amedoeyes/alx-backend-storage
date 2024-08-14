#!/usr/bin/env python3

"""Redis"""

from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def count_calls(method: Callable) -> Callable:
    """Decorator that increments the count for a method"""

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """Wrapper function"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator that stores the history of inputs and outputs for a method"""

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        in_key = "{}:inputs".format(method.__qualname__)
        out_key = "{}:outputs".format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output

    return invoker


def replay(fn: Callable) -> None:
    """Display the history of calls of a particular function"""

    if fn is None or not hasattr(fn, "__self__"):
        return
    redis_store = getattr(fn.__self__, "_redis", None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = "{}:inputs".format(fxn_name)
    out_key = "{}:outputs".format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print("{} was called {} times:".format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print(
            "{}(*{}) -> {}".format(
                fxn_name,
                fxn_input.decode("utf-8"),
                fxn_output,
            )
        )


class Cache:
    """Cache class"""

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store a value"""
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(
        self,
        key: str,
        fn: Callable = None,
    ) -> Union[str, bytes, int, float]:
        """Get a value"""
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """Get a string"""
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Get an int"""
        return self.get(key, lambda x: int(x))
