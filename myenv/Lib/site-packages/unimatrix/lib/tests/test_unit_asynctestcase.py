# pylint: skip-file
import unittest

from ..test import AsyncTestCase


class AsyncTestCaseMethodTestCase(AsyncTestCase):

    @unittest.expectedFailure
    async def test_can_run_async_test_method(self):
        self.fail()



class AsyncTestCaseSetupTestCase(AsyncTestCase):

    async def setUp(self):
        self.foo = 1

    def test_setup_is_ran_async(self):
        self.assertTrue(hasattr(self, 'foo'))

    async def tearDown(self):
        self.assertTrue(self.foo == 1)
