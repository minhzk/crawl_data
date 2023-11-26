"""The :mod:`unimatrix.const` module declares all constants defined by the
Unimatrix framework.
"""
import os
import tempfile


# Specifies the default database connection. If
# ``DB_CONNECTION`` is ``None``, then it is up
# to the implementation to decide.
DB_CONNECTION = os.getenv('DB_CONNECTION')

#: The deployment environment.
DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENV')

#: Directory holding application configuration files.
ETCDIR = os.path.abspath(os.getenv('APP_ETCDIR') or 'etc/')

RUNDIR = os.getenv('APP_RUNDIR', '/opt/app')

LIBDIR = os.getenv('APP_LIBDIR',
    os.path.join(RUNDIR, 'lib'))

#: RSA private key that is used for SSL in local development.
LOCALHOST_SSL_KEY = os.getenv('LOCALHOST_SSL_KEY')

#: X.509 certificate that is used for SSL in local development.
LOCALHOST_SSL_CRT = os.getenv('LOCALHOST_SSL_CRT')

PKIDIR = os.getenv('APP_PKIDIR',
    os.path.join(RUNDIR, 'pki'))

SECDIR = os.getenv('APP_SECDIR',
    '/var/run/secrets/unimatrixone.io')

# Instructs all implementation code to make sure that
# TLS is used with network connections, if possible.
TLS_ENFORCE = not os.getenv('DISABLE_TLS_ENFORCE') == '1'

TMPDIR = tempfile.gettempdir()

#: The location of the Unimatrix Configuration File.
UNIMATRIX_CONFIG_FILE = os.getenv('UNIMATRIX_CONFIG_FILE') or 'app.conf'

VARDIR = os.getenv('APP_VARDIR', '/var/lib/app')
