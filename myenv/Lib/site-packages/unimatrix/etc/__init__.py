"""The :mod:`unimatrix.ext.etc` module provides an API
to load editable text configuration.


Installation
============
Install :mod:`unimatrix.ext.etc` using ``pip``:

.. code:: bash

  pip install --upgrade unimatrix.ext.etc


Usage
=====


Public API
==========

.. autofunction:: read
"""
from .template import read


__all__ = ['read']
