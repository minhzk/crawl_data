#pylint: skip-file
import unittest

from .basetestselection import BaseTestSelectionTestCase


class TestStageSelectionTestCase(unittest.TestCase, BaseTestSelectionTestCase):

    def test_class_is_not_skipped_when_current_stage_matches(self):
        self.assertTestDecorator(False, self.get_class, 'foo', current_stage='foo')

    def test_class_is_skipped_when_current_stage_is_not_test_stage(self):
        self.assertTestDecorator(True, self.get_class, 'foo', current_stage='bar')

    def test_class_is_skipped_when_no_stage_specified(self):
        self.assertTestDecorator(True, self.get_class, 'foo', current_stage=None)

    def test_method_is_not_skipped_when_current_stage_matches(self):
        self.assertTestDecorator(False, self.get_method, 'foo', current_stage='foo')

    def test_method_is_skipped_when_current_stage_is_not_test_stage(self):
        self.assertTestDecorator(True, self.get_method, 'foo', current_stage='bar')

    def test_method_is_skipped_when_no_stage_specified(self):
        self.assertTestDecorator(True, self.get_method, 'foo', current_stage=None)
