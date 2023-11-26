"""Declares an interface to load editable text configuration."""
import glob
import os

import jinja2
import yaml

from unimatrix.const import ETCDIR
from unimatrix.const import UNIMATRIX_CONFIG_FILE
from .datastructures import DTO


environment = jinja2.Environment( # nosec
    autoescape=False,
    variable_start_string="${",
    variable_end_string="}"
)


def render(text, **params):
    """Renders the editable text configuration `text`."""
    t = environment.from_string(text)
    return t.render(env=os.environ, **params)


def load(path: str, *args, **kwargs) -> dict:
    """Loads the configuration from the specified path."""
    if not os.path.isabs(path):
        path = os.path.join(ETCDIR, path)
    if not os.path.exists(path):
        return None
    files = list([path] if not os.path.isdir(path) else glob.glob(f'{path}/*'))
    etc = {}
    for fn in sorted(files):
        with open(fn, 'r') as f:
            etc.update(yaml.safe_load(render(f.read(), **kwargs)))
    return DTO.fromdict(etc)


def unimatrix():
    """Loads settings from the Unimatrix Configuration File."""
    cfg = load(UNIMATRIX_CONFIG_FILE)
    if cfg is None:
        return None

    include_paths = cfg.get('include')
    exc = ValueError(".include must be a list of strings")
    if include_paths is not None\
    and not isinstance(include_paths, list):
        raise exc

    # Iterate of the items and update the configuration loaded from the
    # default UNIMATRIX_CONFIG_FILE.
    for path in include_paths: # pragma: no cover
        if not isinstance(path, str):
            raise exc
        cfg.update(load(path) or {})

    return cfg


app = unimatrix() or DTO()
