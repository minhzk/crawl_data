"""Declares functions to assist in the configuration of an application."""
import importlib
import inspect
import os
import sys

from unimatrix.exceptions import ImproperlyConfigured


def for_environment(qualname, defaults='defaults', env=None):
    """Use the deployment environment to set up a Unimatrix settings module.
    The package specified by `qualname` is assumed to contain submodules for
    different environments, and a module holding the default settings.

    The settings are constructed by importing the defaults, and then the
    environment-specific settings. These are then added to the package
    specified by `qualname`. If no environment-specific settings are present
    (i.e. they could not be imported), then this is silently ignored. It is
    assumed that the defaults contain all settings to properly run an
    application.

    Args:
        qualname: the qualified name of the Python package holding the
            submodules for each environment.
        defaults: the submodule holding the defaults. Default is ``defaults``.
        env: optionally specify the current deployment environment. Otherwise
            the ``DEPLOYMENT_ENV`` variable is used to determine the
            environment.

    Returns:
        None
    """
    # Bail out early if the settings are already configured.
    if getattr(sys.modules[qualname], 'SETTINGS_CONFIGURED', False):
        return

    env = env or os.getenv('DEPLOYMENT_ENV')
    if env is None:
        raise ImproperlyConfigured(
            "Unable to determine the deployment environment. "
            "Provide the `env` argument or set the `DEPLOYMENT_ENV` "
            " environment variable."
        )

    try:
        defaults = importlib.import_module("%s.defaults" % qualname)
    except ImportError:
        raise ImproperlyConfigured("Unable to import %s.defaults" % qualname)
    settings = sys.modules[qualname]
    for key, value in inspect.getmembers(defaults):
        if not str.isupper(key):
            continue
        setattr(settings, key, value)

    # Try to import the environment-specific settings. Silently ignore
    # import errors (these suggest that the current environment does not
    # have specific settings that differ from the defaults).
    try:
        environment_settings = importlib.import_module(
            '%s.%s' % (qualname, env))
        for key, value in inspect.getmembers(environment_settings):
            if not str.isupper(key):
                continue
            setattr(settings, key, value)
    except ImportError:
        pass

    # Indicate that the settings are configured to prevent ending up in
    # infinite loops.
    settings.SETTINGS_CONFIGURED = True
