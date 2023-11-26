#pylint: skip-file
import unittest

from ..test import TestCaseSelector
from .basetestselection import BaseTestSelectionTestCase


class TestScopeSelectionTestCase(unittest.TestCase, BaseTestSelectionTestCase):

    def test_class_is_not_skipped_when_current_scope_in_scopes(self):
        self.assertTestDecorator(False, self.get_class, 'foo', scopes=['bar'],
            current_stage='foo', current_scope='bar')

    def test_class_is_not_skipped_when_current_scope_in_multiple_scopes(self):
        self.assertTestDecorator(False, self.get_class, 'foo',
            scopes=['bar', 'baz'], current_stage='foo', current_scope='bar')

    def test_class_is_skipped_when_scopes_are_not_defined(self):
        self.assertTestDecorator(True, self.get_class, 'foo', scopes=None,
            current_stage='foo', current_scope='bar')

    def test_class_is_skipped_when_current_scope_is_not_in_defined_scopes_empty(self):
        self.assertTestDecorator(True, self.get_class, 'foo', scopes=[],
            current_stage='foo', current_scope='bar')

    def test_class_is_skipped_when_current_scope_is_not_in_defined_scopes(self):
        self.assertTestDecorator(True, self.get_class, 'foo', scopes=['baz'],
            current_stage='foo', current_scope='bar')

    def test_class_is_skipped_when_current_scope_is_none(self):
        self.assertTestDecorator(True, self.get_class, 'foo', scopes=['baz'],
            current_stage='foo', current_scope=None)

    def test_scope_decorator_skips(self):
        selector = TestCaseSelector('foo', current_stage='foo', scopes=[],
            current_scope='bar')

        @selector.scope('bar')
        def f(*args, **kwargs):
            pass

        self.assertTestNotSkipped(f)
