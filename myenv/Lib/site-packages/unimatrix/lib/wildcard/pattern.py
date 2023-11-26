"""Declares :class:`Pattern`."""
import itertools


class Pattern:
    """Represents a matching pattern, possible containing wildcards."""

    @staticmethod
    def compare(pattern, value, sep='.'):
        """Compare `pattern` against `value` using the separator character
        `sep`.
        """
        if pattern == value:
            return True

        eq = None
        for x, y in itertools.zip_longest(
            str.split(pattern, sep),
            str.split(value, sep)
        ):
            if None in (x, y):
                # If any of the items is None, it means that the patterns
                # did not have the same length.
                eq = False
                break
            if (x == y) or (x == '*'):
                continue
            eq = False
            break
        else:
            eq = True
        assert eq is not None # nosec
        return eq

    def __init__(self, pattern: str, sep: str):
        self.pattern = pattern
        self.sep = sep

    def is_match(self, value: str) -> bool:
        """Return a boolean indicating if the pattern matches the value."""
        result = self.compare(self.pattern, value, self.sep)
        return result

    def __str__(self) -> str:
        return self.pattern

    def __eq__(self, value) -> bool:
        return self.is_match(value)

    def __hash__(self) -> int:
        return hash(self.pattern)
