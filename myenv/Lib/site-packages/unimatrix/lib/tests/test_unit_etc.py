# pylint: skip-file
import os
import tempfile
import unittest

from .. import etc


class EditableTextConfigurationTestCase(unittest.TestCase):

    def test_load(self):
        cfg = etc.load('app.conf')
        self.assertIn('secrets', cfg)
        self.assertIn('include', cfg)
        self.assertEqual(cfg.include[0], 'conf.d')

    def test_load_unimatrix(self):
        cfg = etc.app
        self.assertIn('foo', cfg)
        self.assertIn('secrets', cfg)
        self.assertIn('include', cfg)
        self.assertEqual(cfg.include[0], 'conf.d')
        self.assertEqual(cfg.foo, 'bar')

    def test_load_nonexisting(self):
        cfg = etc.load('does-not-exist.conf')
        self.assertEqual(cfg, None)

    def test_load_fragments(self):
        cfg = etc.load('conf.d')
        self.assertIn('secrets', cfg)
        self.assertIn('foo', cfg.secrets)
        self.assertEqual(cfg.secrets.foo, 'bar')

    def test_render_with_variable(self):
        value = etc.render('${foo}', foo='bar')
        self.assertEqual(value, 'bar')

    def test_render_environment_variable(self):
        os.environ['FOO'] = 'bar'
        value = etc.render('${env.FOO}')
        self.assertEqual(value, 'bar')

    def test_load_simple(self):
        with tempfile.NamedTemporaryFile('w+') as f:
            f.write(
                'foo:\n'
                '  bar: 1'
            )
            f.seek(0)
            data = etc.load(f.name)
        self.assertIn('foo', data)
        self.assertIn('bar', data['foo'])
        self.assertEqual(data['foo']['bar'], 1)

    def test_load_simple(self):
        os.environ['FOO'] = 'bar'
        with tempfile.NamedTemporaryFile('w+') as f:
            f.write(
                'foo: ${env.FOO}\n'
            )
            f.seek(0)
            data = etc.load(f.name)
        self.assertIn('foo', data)
        self.assertEqual(data['foo'], 'bar')
