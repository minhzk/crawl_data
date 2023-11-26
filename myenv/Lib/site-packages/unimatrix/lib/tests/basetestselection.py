#pylint: skip-file
import types
import unittest

from ..test import TestCaseSelector


class BaseTestSelectionTestCase:

    def get_class(self, skip, *args, **kwargs):
        scopes = kwargs.pop('scopes', None)
        selector = TestCaseSelector(*args, **kwargs)

        @selector.scopes(scopes)
        class mock_class:
            def test_mock_method(*args):
                if skip:
                    self.fail("This method should be skipped.")
        return mock_class

    def get_method(self, skip, *args, **kwargs):
        scopes = kwargs.pop('scopes', None)
        selector = TestCaseSelector(*args, **kwargs)

        class mock_class:
            @selector.scopes(scopes)
            def test_mock_method(*args):
                if skip:
                    self.fail("This method should be skipped.")
        return mock_class().test_mock_method

    def assertTestSkipped(self, testcase):
        if isinstance(testcase, type):
            return self.assertTrue(getattr(testcase, '__unittest_skip__', True))
        try:
            testcase()
        except unittest.SkipTest:
            pass
        else:
            self.fail("Test was ran but should be skipped.")

    def assertTestNotSkipped(self, testcase):
        if isinstance(testcase, type):
            return self.assertFalse(getattr(testcase, '__unittest_skip__', False))
        try:
            testcase()
        except unittest.SkipTest:
            self.fail("Test was skipped but should be ran.")

    def assertTestDecorator(self, skip, factory, *args, **kwargs):
        decoratable = factory(skip, *args, **kwargs)
        return self.assertTestSkipped(decoratable)\
            if skip else self.assertTestNotSkipped(decoratable)
