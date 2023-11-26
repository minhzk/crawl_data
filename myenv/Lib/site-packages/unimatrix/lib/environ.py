"""Declares primitives to parse data from the operating
system environment.
"""
import os
from typing import Callable
from typing import Mapping
from typing import Sequence

from unimatrix.exceptions import ImproperlyConfigured


def parseint(environ, key, default):
    """Parse the environment variable as an integer."""
    try:
        return int(environ.get(key) or default)
    except ValueError:
        raise ImproperlyConfigured('%s can not be cast to integer.' % key)

def parsebool(environ, key):
    """Parses the environment variable into a boolean."""
    return str.lower(environ.get(key) or '') in ('1', 'yes', 'y', 'enabled')


def parsefilepath(environ, key, default=None):
    """Parses a filepath. If the key does not exist, or the file pointed to
    by the environment variable does not exist, return ``None``.

    The `default` argument specifies a default value if the file does not
    exist at the locatio specified by the key, or the key was absent.
    """
    fp = environ.get(key)
    if fp is not None and not os.path.exists(fp):
        fp = None
    if not fp and default and os.path.exists(default):
        fp = default
    return fp


def parselist(
    environ: Mapping[str, str],
    key: str,
    sep: str = ':',
    cls: Callable[..., Sequence[str]] = tuple
) -> Sequence[str]:
    """Parses the environment variable into an iterable,
    using `sep` as a separator e.g.::

    >>> from unimatrix.lib.environ import parselist
    >>> parselist({'foo': '1:2'}, 'foo')
    ('1', '2')
    """
    values = environ.get(key) or ''
    return cls(filter(bool, str.split(values, sep)))
