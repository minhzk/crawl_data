# pylint: skip-file
import time
import unittest

from .. import timezone


class CurrentTimeTestCase(unittest.TestCase):

    def test_now_increases_over_time(self):
        t1 = timezone.now()
        time.sleep(0.1)
        t2 = timezone.now()
        self.assertGreater(t2, t1)
