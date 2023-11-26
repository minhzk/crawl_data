# pylint: skip-file
import asyncio
import unittest
import time

from .. import security


class ConstantExecutionTestCase(unittest.TestCase):

    def execute_time(self, t):
        async def f():
            t1 = time.time()
            async with security.constant(t):
                pass
            self.assertTrue((time.time() - t1) >= t)
        asyncio.run(f())

    def test_constant_execution_2(self):
        self.execute_time(2)

    def test_constant_execution_4(self):
        self.execute_time(4)
