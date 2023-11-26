# pylint: disable=line-too-long
"""Specifies the default logging configuration for Unimatrix
applications.
"""
import copy
import logging.config
import os
import sys


DEFAULT_LOG_LEVEL = 'ERROR'

DEPLOYMENT_ENV = os.getenv('DEPLOYMENT_ENV') or 'production'

DEFAULT_MSG_FMT = '%(message)s'
if DEPLOYMENT_ENV == 'local':
    DEFAULT_MSG_FMT = '%(pathname)s:%(lineno)d - %(message)s'
if not sys.stdout.isatty():
    DEFAULT_MSG_FMT = "%(levelprefix)s %(message)"

LOG_LEVEL = os.getenv('LOG_LEVEL') or 'WARNING'

SYSLOG_HOST = os.getenv('SYSLOG_HOST') or 'localhost'

SYSLOG_PORT = int(os.getenv('SYSLOG_PORT') or 5140)


LOGGING: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "unimatrix.lib.logging.DefaultFormatter",
            "fmt": DEFAULT_MSG_FMT,
            "use_colors": None,
        },
        "access": {
            "()": "unimatrix.lib.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "error": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "unimatrix": {"handlers": ["default"], "level": LOG_LEVEL},
        "unimatrix.error": {"handlers": ["error"], "level": "INFO"},
        "unimatrix.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}


def configure(loggers=None):
    """Configure loggers."""
    defaults = copy.deepcopy(LOGGING)
    defaults['loggers'].update(loggers or {})
    logging.config.dictConfig(defaults)
