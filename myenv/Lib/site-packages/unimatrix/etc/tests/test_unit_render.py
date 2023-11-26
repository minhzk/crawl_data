# pylint: skip-file
import unittest

import yaml

from ..template import read
from ..template import render


class RenderTestCase(unittest.TestCase):

    def test_render_with_variable_from_env(self):
        value = 'foo'
        template = '${env.FOO}'
        result = render(template, env={'FOO': value})
        self.assertEqual(result, value)

    def test_render_with_variable(self):
        value = 'foo'
        template = '${foo}'
        result = render(template, foo=value)
        self.assertEqual(result, value)

    def test_read_from_filepath(self):
        etc = read(
            'etc/test_read_from_filepath.yml',
            env={'BAR': '1'}
        )
        dto = yaml.safe_load(etc)
        self.assertIn('foo', dto)
        self.assertEqual(dto['foo'], 1)
