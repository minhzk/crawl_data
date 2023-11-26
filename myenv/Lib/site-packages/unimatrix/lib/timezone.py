"""Provides an API for date and time related functions."""
import datetime


def now():
    """Return the current date and time, represented as milliseconds since the
    UNIX epoch.
    """
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
