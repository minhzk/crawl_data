# pylint: skip-file
import asyncio
import unittest

from .. import meta


class AllowSyncDecoratorTestCase(unittest.TestCase):

    def test_run_async_function_sync(self):
        result = foo, bar, *_ = async_function.sync('bar')
        self.assertEqual(foo, 'foo')
        self.assertEqual(bar, 'bar')


@meta.allow_sync
async def async_function(arg, *args, **kwargs):
    return 'foo', arg, args, kwargs
