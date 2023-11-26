"""Declares :class:`PatternSet`."""
import collections.abc
import typing

from .pattern import Pattern


class PatternSet(collections.abc.Set):

    def __init__(self, patterns: set, sep: str = "."):
        self.patterns = set([Pattern(x, sep) for x in patterns])

    def __and__(self, value: set) -> set:
        return set(str(x) for x in super().__and__(value))

    def __rand__(self, value: set):
        return self & value

    def __contains__(self, value) -> bool:
        contains = None
        for pattern in self.patterns:
            if not pattern.is_match(value):
                continue
            contains = True
            break
        else:
            contains = False
        assert contains is not None # nosec
        return contains

    def __len__(self) -> int:
        return len(self.patterns)

    def __iter__(self):
        return iter(self.patterns)
