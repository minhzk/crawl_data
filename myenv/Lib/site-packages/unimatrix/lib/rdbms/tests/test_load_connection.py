# pylint: skip-file
import os
import tempfile
import unittest

import yaml

from ..config import load


class DatabaseConnectionLoaderTestCase(unittest.TestCase):
    connections = [
        ('foo', {
            'engine': 'postgresql',
            'host': 'remote-host',
            'port': 2345,
            'name': 'dbname',
            'user': 'dbuser',
            'password': 'dbpassword'
        })
    ]

    def setUp(self):
        self.secdir = tempfile.mkdtemp()

        # Create some example database connections of various types.
        for name, params in self.connections:
            with open(os.path.join(self.secdir, name), 'w') as f:
                f.write(yaml.safe_dump(params))

    def test_load_raises_valuerror_with_config_and_no_default(self):
        with self.assertRaises(ValueError):
            load(config_dir=self.secdir)

    def test_load_connections_from_secdir(self):
        connections = load(config_dir=self.secdir,
            env={'DB_DEFAULT_CONNECTION': 'foo'})

    def test_load_connections_default_connection_is_set(self):
        connections = load(config_dir=self.secdir,
            env={'DB_DEFAULT_CONNECTION': 'foo'})
        self.assertEqual(connections['self'], connections['foo'])

    def test_load_connections_from_secdir_raises_on_non_existing_default(self):
        with self.assertRaises(LookupError):
            connections = load(config_dir=self.secdir,
                env={'DB_DEFAULT_CONNECTION': 'baz'})

    def test_default_connection_is_self(self):
        connections = load({
            'DB_ENGINE': 'sqlite',
            'DB_NAME': ':mem:'
        })
        self.assertIn('self', connections)
        self.assertEqual(len(connections.keys()), 1)
