import typing as t
import functools


class KwargsCache:
    def __init__(self):
        self._kwargs_cache: t.Dict[str, t.Dict[str, t.Any]] = dict()

    def get_cached_kwargs(self, cache_key: str):
        return self._kwargs_cache[cache_key]

    @staticmethod
    def save_function_kwargs(cache_key: str):
        def deco(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                self._kwargs_cache[cache_key] = kwargs
                return func(self, *args, **kwargs)

            return wrapper

        return deco
