# pylint: skip-file
import unittest

from ..config import parse_environment


class ParseEnvironmentTestCase(unittest.TestCase):

    def test_unsupported_engine_raises_valueerror(self):
        env = {
            'DB_ENGINE': 'foo',
        }
        with self.assertRaises(ValueError):
            opts = parse_environment(env)

    def test_parse_autocommit_enabled(self):
        opts = parse_environment({})
        self.assertEqual(opts, None)
        env = {
            'DB_ENGINE': 'postgresql',
            'DB_AUTOCOMMIT': '1'
        }
        opts = parse_environment(env)
        self.assertTrue(opts.autocommit)

    def test_parse_autocommit_disabled(self):
        opts = parse_environment({})
        self.assertEqual(opts, None)
        env = {
            'DB_ENGINE': 'postgresql',
            'DB_AUTOCOMMIT': '0'
        }
        opts = parse_environment(env)
        self.assertFalse(opts.autocommit)

    def test_parse_postgresql_with_defaults(self):
        env = {
            'DB_ENGINE': 'postgresql',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 5432)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)

    def test_parse_mysql_with_defaults(self):
        env = {
            'DB_ENGINE': 'mysql',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 3306)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)

    def test_parse_sqlite_with_defaults(self):
        env = {
            'DB_ENGINE': 'sqlite',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, None)
        self.assertEqual(opts.port, None)
        self.assertEqual(opts.name, ":memory:")
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)

    def test_parse_mssql_with_defaults(self):
        env = {
            'DB_ENGINE': 'mssql',
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 1433)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)
        self.assertEqual(opts.options.driver, "ODBC Driver 17 for SQL Server")
        self.assertEqual(opts.options.unicode_results, True)

    def test_parse_mssql_with_db_driver(self):
        env = {
            'DB_ENGINE': 'mssql',
            'DB_DRIVER': "ODBC Driver 13 for SQL Server"
        }
        opts = parse_environment(env)
        self.assertEqual(opts.host, 'localhost')
        self.assertEqual(opts.port, 1433)
        self.assertEqual(opts.name, None)
        self.assertEqual(opts.username, None)
        self.assertEqual(opts.password, None)
        self.assertEqual(opts.options.driver, "ODBC Driver 13 for SQL Server")
        self.assertEqual(opts.options.unicode_results, True)
