# pylint: skip-file
import unittest.mock


def sync_func(name, *args, **kwargs):
    return args, kwargs


async def func(name, *args, **kwargs):
    return args, kwargs


async def boot(*args, **kwargs):
    return args, kwargs


async def shutdown(*args, **kwargs):
    return args, kwargs
