import typing as t
import inspect
import functools


def discard_unknown_args(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        allowed_parameters = [p for p in signature.parameters]
        proper_kwargs = {
            k: v for k, v in kwargs.items() if k in allowed_parameters
        }
        return func(*args, **proper_kwargs)

    return wrapper
