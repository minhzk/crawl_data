# pylint: skip-file
import unittest

from .. import test


class CapabilitiesDiscoveryTestCase(unittest.TestCase):

    @test.needs('never-runs')
    def test_skipped_test(self):
        self.fail("Test was not skipped.")

    @test.needs('noop')
    def test_not_skipped(self):
        pass
