# pylint: skip-file
import typing

from .patternset import PatternSet


__all__ = ['matches']


def matches(
    patterns: typing.Union[str, typing.Set[str] ],
    values: typing.Union[str, typing.Set[str] ],
    sep: str = '.'
) -> set:
    """Matches `patterns` against `values` using the separator character
    `sep`. The input parameters may be either strings or iterables containing
    strings. Return a set containing the matches.
    """
    if isinstance(patterns, str):
        patterns = {patterns}
    patterns = PatternSet(patterns, sep)
    if isinstance(values, str):
        values = {values}
    return patterns & values
