# pylint: skip-file
import unittest
from unittest.mock import MagicMock
from unittest.mock import AsyncMock

from unimatrix.lib.datastructures import DTO
from unimatrix.lib.test import AsyncTestCase
from unimatrix import runtime


class RuntimeEventsTestCase(unittest.TestCase):

    def setUp(self):
        self.get_entrypoints = runtime.get_entrypoints
        runtime.IS_CONFIGURED = False

    def tearDown(self):
        runtime.get_entrypoints = self.get_entrypoints
        runtime.IS_CONFIGURED = False

    def test_setup_with_sync_function_calls_on_setup(self):
        pkg = ['foo', DTO(
            on_setup=MagicMock()
        )]
        runtime.get_entrypoints = MagicMock(return_value=[pkg])
        runtime.setup.sync()
        pkg[1].on_setup.assert_called_once()

    def test_setup_with_async_function_calls_on_setup(self):
        mock = AsyncMock()
        async def f():
            await mock()
            
        pkg = ['foo', DTO(
            on_setup=f
        )]
        runtime.get_entrypoints = MagicMock(return_value=[pkg])
        runtime.setup.sync()
        mock.assert_called_once()

    def test_setup_with_sync_function_sets_configured(self):
        runtime.setup.sync()
        self.assertTrue(runtime.IS_CONFIGURED)

    def test_teardown_with_sync_function_sets_configured(self):
        runtime.teardown.sync()
        self.assertFalse(runtime.IS_CONFIGURED)

    def test_teardown_with_sync_function_calls_on_teardown(self):
        pkg = ['foo', DTO(
            on_teardown=MagicMock()
        )]
        runtime.get_entrypoints = MagicMock(return_value=[pkg])
        runtime.teardown.sync()
        pkg[1].on_teardown.assert_called_once()

    def test_teardown_with_async_function_calls_on_teardown(self):
        mock = AsyncMock()
        async def f():
            await mock()
            
        pkg = ['foo', DTO(
            on_teardown=f
        )]
        runtime.get_entrypoints = MagicMock(return_value=[pkg])
        runtime.teardown.sync()
        mock.assert_called_once()
