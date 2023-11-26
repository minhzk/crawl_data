"""Exposes functions and attributes related to the rendering
of templates.
"""
import os

import jinja2


environment = jinja2.Environment( # nosec
    autoescape=False,
    variable_start_string="${",
    variable_end_string="}"
)


def render(text: str, **params) -> str:
    """Renders the editable text configuration `text`."""
    t = environment.from_string(text)
    params.setdefault('env', os.environ)
    return t.render(**params)


def read(
    fn: str,
    encoding: str = 'utf-8',
    **params
) -> str:
    """Read file from `fn`."""
    with open(fn, 'rb') as f:
        return render(bytes.decode(f.read(), encoding), **params)
