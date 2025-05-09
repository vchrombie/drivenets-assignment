import types
from collections.abc import Iterable


def check_type_equality(left, right) -> bool:
    """True indicates the 2 types are the same"""
    if isinstance(right, types.GenericAlias):
        right_t_args = (
            right.__args__[0]
            if isinstance(right.__args__, tuple)
            else right.__args__
        )
        right_t_origin = right.__origin__
        if type(left) != right_t_origin:
            return False
        if isinstance(left, Iterable):
            return all(isinstance(item, right_t_args) for item in left)
    return isinstance(left, right)
