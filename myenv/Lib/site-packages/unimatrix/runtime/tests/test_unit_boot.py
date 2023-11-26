# pylint: skip-file
import os
import unittest

import unimatrix.runtime

from . import mock_boot_module as mocks



class BootModuleTestCase(unittest.TestCase):

    def setUp(self):
        if hasattr(mocks, 'func'):
            delattr(mocks, 'func')
        os.environ.pop('UNIMATRIX_BOOT_MODULE', None)

    @unittest.expectedFailure
    def test_sync_callable(self):
        os.environ['UNIMATRIX_BOOT_MODULE'] = 'unimatrix.runtime.tests.mock_boot_module.sync_func'
        args, kwargs = unimatrix.runtime.on.sync('boot', 1, foo=1)
        self.assertIn(1, args)
        self.assertIn('foo', kwargs)

    @unittest.expectedFailure
    def test_callable(self):
        os.environ['UNIMATRIX_BOOT_MODULE'] = 'unimatrix.runtime.tests.mock_boot_module.func'
        args, kwargs = unimatrix.runtime.on.sync('boot', 1, foo=1)
        self.assertIn(1, args)
        self.assertIn('foo', kwargs)

    def test_module_boot(self):
        os.environ['UNIMATRIX_BOOT_MODULE'] = 'unimatrix.runtime.tests.mock_boot_module'
        args, kwargs = unimatrix.runtime.on.sync('boot', 1, foo=1)
        self.assertIn(1, args)
        self.assertIn('foo', kwargs)

    def test_module_shutdown(self):
        os.environ['UNIMATRIX_BOOT_MODULE'] = 'unimatrix.runtime.tests.mock_boot_module'
        args, kwargs = unimatrix.runtime.on.sync('shutdown', 1, foo=1)
        self.assertIn(1, args)
        self.assertIn('foo', kwargs)
