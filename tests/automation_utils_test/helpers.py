import typing
import collections


def equals_ignore_ordering(
    iterable1: typing.Iterable[typing.Any],
    iterable2: typing.Iterable[typing.Any],
) -> bool:
    return collections.Counter(iterable1) == collections.Counter(iterable2)
