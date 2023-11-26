"""Provides the base functionalities to configure a database connection from
environment variables or configuration files.
"""
import copy
import os

import dsnparse
import yaml

from unimatrix.const import SECDIR
from unimatrix.lib.datastructures import DTO


__all__ = ['parse_environment']


def _parse_bool(value):
    return (value == '1') if value is not None else None


ENVIRONMENT_VARIABLES = [
    ('DB_HOST', 'host', False, str),
    ('DB_PORT', 'port', False, int),
    ('DB_NAME', 'name', False, str),
    ('DB_USERNAME', 'username', False, str),
    ('DB_PASSWORD', 'password', False, str),
    ('DB_CONNECTION_MAX_AGE', 'max_age', False, int),
    ('DB_AUTOCOMMIT', 'autocommit', False, _parse_bool)
]


#: Default values by engine.
DEFAULTS = {
    'postgresql': {
        'host': "localhost",
        'port': 5432,
    },
    'mysql': {
        'host': "localhost",
        'port': 3306,
    },
    'sqlite': {
        'name': ":memory:"
    },
    'mssql': {
        'host': 'localhost',
        'port': 1433,
        'options': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        }
    }
}


class DataSourceName(dsnparse.ParseResult):

    @property
    def admin(self) -> str:
        """Return the DSN used for an administrative connection (e.g. to
        create a new database if it does not exist yet).
        """
        return self.replace(path='')

    @property
    def name(self) -> str:
        return str.lstrip(self.path or '', '/') or None

    @property
    def test(self) -> str:
        """Return the DSN for a transient testing database connection."""
        if self.scheme == 'sqlite':
            return DataSourceName('sqlite://')
        if self.name is None:
            raise ValueError("Must specify a database name.")
        return self.replace(path=self.generate_test_name())

    @classmethod
    def verify(cls, dsn):
        pass

    @property
    def hostloc(self):
        hostloc = self.hostname
        if self.port:
            hostloc = '{hostloc}:{port}'.format(hostloc=hostloc, port=self.port)
        return hostloc or 'localhost'

    def generate_test_name(self) -> str:
        """Return a string containing a unique name for a transient testing
        database.
        """
        return f'test_{bytes.hex(os.urandom(3))}'

    def replace(self, **kwargs):
        """Replace the parameters specified in the keyword arguments and
        return a new instance.
        """
        scheme = kwargs.setdefault('scheme', self.scheme)
        hostname = kwargs.setdefault('hostname', self.hostname)
        params = self.parse(self.geturl())
        params.pop('dsn')
        return dsnparse.parse(
            f'{scheme}://{hostname}',
            parse_class=type(self), **{**params, **kwargs})


def encode_dsn(opts: DTO) -> str:
    """Encodes the database configuration into a Data Source Name (DSN)."""
    dsn = dsnparse.parse(f'{opts.engine}://', DataSourceName)
    if opts.engine == 'sqlite':
        if opts.host is None:
            dsn.setdefault('hostname', '/')
        if opts.get('name') not in (':mem:', ':memory:', None):
            dsn.setdefault('hostname', opts.name)
    else:
        dsn.setdefault('username', opts.get('username') or '')
        dsn.setdefault('password', opts.get('password') or '')
        dsn.setdefault('path', opts.get('name') or '')
        if opts.host is not None:
            dsn.setdefault('hostname', opts.host)

    if opts.engine == 'postgresql':
        dsn.setdefault('port', opts.get('port') or 5432)
    elif opts.engine == 'mssql':
        dsn.setdefault('port', opts.get('port') or 1433)
    elif opts.engine == 'mysql':
        dsn.setdefault('port', opts.get('port') or 3306)
    elif opts.engine == 'sqlite':
        pass
    else:
        raise NotImplementedError(opts.engine)
    if opts.engine != 'sqlite':
        assert dsn.hostname is not None
    return dsn


def parse_environment(env):
    """Parses a database connection from the operating system
    environment based on the ``DB_*`` variables. Return a
    datastructure containing the configuration, or ``None`` if
    it was not defined.
    """
    # If no engine is specified, then the application does not
    # get its database connection configuration from environment
    # variables.
    engine = env.get('DB_ENGINE')
    if engine is None:
        return None

    if engine not in DEFAULTS:
        raise ValueError("Unsupported DB_ENGINE: %s" % engine)

    opts = DTO(engine=engine, options={})
    for name, attname, required, cls in ENVIRONMENT_VARIABLES:
        default = DEFAULTS[engine].get(attname)
        value = env.get(name)
        if value is None:
            value = default
        opts[attname] = cls(value) if value is not None else value
        assert not required #nosec

        if DEFAULTS[engine].get('options'):
            opts['options'] = copy.deepcopy(DEFAULTS[engine]['options'])

        # Engine specific - FIXME
        if engine == 'mssql':
            if env.get('DB_DRIVER'):
                opts['options']['driver'] = env['DB_DRIVER']

        opts['dsn'] = encode_dsn(opts)

    opts.engine = engine
    return opts.as_dto()


def load(env=None, config_dir=None):
    """Loads the configured database connections from the operating
    system environment variables and the Unimatrix configuration files.

    Database connections are loaded with the following precedence:

    - Environment variables
    - Unimatrix Database Connection (UDC) files.

    Args:
        env (dict): a dictionary holding environment variables. Defaults
            to ``os.environ``.
        config_dir (str): a directory on the local filesystem holding
            the database connection configuration files. Defaults to
            `SECDIR/rdbms/connections`.

    Returns:
        dict
    """
    env = copy.deepcopy(env or os.environ)
    config_dir = config_dir or os.path.join(SECDIR, 'rdbms/connections')
    default_connection = env.get('DB_DEFAULT_CONNECTION')
    use_environment = not bool(os.listdir(config_dir))\
        if os.path.exists(config_dir) else True
    if not use_environment and not default_connection:
        raise ValueError("Set the DB_DEFAULT_CONNECTION environment variable.")
    connections = {}
    if use_environment:
        self = parse_environment(env)
        if self:
            connections['self'] = self
    else:
        for fn in os.listdir(config_dir):
            connections[fn] = yaml.safe_load(open(os.path.join(config_dir, fn)))

        if default_connection not in connections:
            raise LookupError(
                "Default connection does not exist: " + default_connection)

        connections['self'] = connections[default_connection]

    return connections
