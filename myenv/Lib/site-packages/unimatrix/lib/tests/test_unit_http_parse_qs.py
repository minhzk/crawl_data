# pylint: skip-file
import unittest

from .. import http


class QueryStringParserTestCase(unittest.TestCase):

    def test_parse_with_scalars(self):
        qs = 'foo=1&bar=2'
        params = http.parse_qs(qs)
        self.assertIn('foo', params)
        self.assertIn('bar', params)
        self.assertEqual(params['foo'], '1')
        self.assertEqual(params['bar'], '2')

    def test_parse_with_list(self):
        qs = 'foo=1&bar=2&bar=3'
        params = http.parse_qs(qs)
        self.assertIn('foo', params)
        self.assertIn('bar', params)
        self.assertEqual(params['foo'], '1')
        self.assertIsInstance(params['bar'], list)
        self.assertEqual(params['bar'][0], '2')
        self.assertEqual(params['bar'][1], '3')

    def test_parse_with_list_intermixed(self):
        qs = 'bar=3&foo=1&bar=2'
        params = http.parse_qs(qs)
        self.assertIn('foo', params)
        self.assertIn('bar', params)
        self.assertEqual(params['foo'], '1')
        self.assertIsInstance(params['bar'], list)
        self.assertIn('2', params['bar'])
        self.assertIn('3', params['bar'])
