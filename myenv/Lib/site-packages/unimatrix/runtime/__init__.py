"""The :mod:`unimatrix.runtime` package provides a common interface to set
up the application runtime environment.
"""
import asyncio
import importlib
import inspect
import pkg_resources
import os
import warnings

from unimatrix.lib import meta
from . import logging


IS_CONFIGURED = False


def get_entrypoints(name):
    entrypoints = [
        (entry_point.name, entry_point.load())
        for entry_point
        in pkg_resources.iter_entry_points(name)
    ]
    return sorted(entrypoints, key=lambda x: getattr(x[1], 'WEIGHT', 0))


def get_settings_module(module_name: str) -> str:
    """Return a string containing the qualified Python name of the Unimatrix
    settings module. The qualified name is retrieved from the environment
    variable ``UNIMATRIX_SETTINGS_MODULE`` or from the standard location of
    ``<app symbol>.runtime.settings``.
    """
    return os.getenv('UNIMATRIX_SETTINGS_MODULE')\
        or f"{str.split(module_name, '.')[0]}.runtime.settings"


def execute(func, *args, **kwargs):
    """Setup the Unimatrix environment and run `func`."""
    async def f():
        await on('boot')
        try:
            return await func(*args, **kwargs)
        finally:
            await on('shutdown')
    return asyncio.run(f())


async def run_entrypoints(
    name: str,
    fn: str = None,
    namespace: str = 'unimatrix.runtime',
    *args, **kwargs) -> None:
    """Runs the entrpoints specified by `name`."""
    qualname = f'{namespace}.{name}'
    for _, entry_point in get_entrypoints(qualname):
        f = entry_point if not fn else getattr(entry_point, fn, None)
        if not callable(f):
            warnings.warn(
                f"Entrypoint {entry_point} (fn: {fn}) was not callable."
            )
            continue
        await f(*args, **kwargs)\
            if inspect.iscoroutinefunction(f)\
            else f(*args, **kwargs)


@meta.allow_sync
async def setup():
    """Setup all :mod:`unimatrix` components."""
    global IS_CONFIGURED
    if IS_CONFIGURED:
        return

    logging.configure()
    await run_entrypoints('init')
    for _, module in get_entrypoints('unimatrix.runtime'):
        on_setup = getattr(module, 'on_setup', None)
        if on_setup is None:
            continue
        await on_setup()\
            if inspect.iscoroutinefunction(on_setup)\
            else on_setup()

    IS_CONFIGURED = True


@meta.allow_sync
async def teardown():
    """Teardown all :mod:`unimatrix` components."""
    for _, module in get_entrypoints('unimatrix.runtime'):
        on_teardown = getattr(module, 'on_teardown', None)
        if on_teardown is None:
            continue
        await on_teardown()\
            if inspect.iscoroutinefunction(on_teardown)\
            else on_teardown()

    IS_CONFIGURED = False # pylint: disable=unused-variable
    await run_entrypoints('cleanup')


async def startup(*args, **kwargs):
    """Shorthand for ``unimatrix.runtime.on('boot')``."""
    return await on('boot', *args, **kwargs)


async def shutdown(*args, **kwargs):
    """Shorthand for ``unimatrix.runtime.on('shutdown')``."""
    return await on('teardown', *args, **kwargs)


@meta.allow_sync
async def on(name, *args, runlevel=None, **kwargs):
    if name == 'boot':
        await setup()
    elif name == 'shutdown':
        await teardown()

    # Before running the event handlers in UNIMATRIX_BOOT_MODULE, run the
    # entrypoints of installed modules.
    for _, module in get_entrypoints(f'unimatrix.runtime.{name}'):
        handler = getattr(module, name, None)
        if handler is None:
            continue
        await handler()\
            if inspect.iscoroutinefunction(handler)\
            else handler()

    qualname = os.getenv('UNIMATRIX_BOOT_MODULE')
    if qualname is None:
        return
    try:
        obj = importlib.import_module(qualname)
    except ImportError:
        warnings.warn(
            f"UNIMATRIX_BOOT_MODULE points to a non-existant symbol: "
            f"{qualname}.")
        return

    if not callable(obj) and not inspect.ismodule(obj):
        raise TypeError(
            "UNIMATRIX_BOOT_MODULE must point to a callable or module."
        )
    if callable(obj):
        return await obj(name, *args, **kwargs)\
            if inspect.iscoroutinefunction(obj)\
            else obj(name, *args, **kwargs)

    f = getattr(obj, name, None)
    if f is None:
        return
    return await f(*args, **kwargs)\
        if inspect.iscoroutinefunction(f)\
        else f(*args, **kwargs)
