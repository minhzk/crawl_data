"""Exposes functions related to HTTP."""
import urllib.parse

from unimatrix.lib.datastructures import DTO


def parse_qs(value):
    """Parses a query string into a dictionary"""
    params = {}
    for key, value in urllib.parse.parse_qsl(value):
        if key in params:
            current = params.pop(key)
            if isinstance(current, str):
                current = [current]
            current.append(value)
            params[key] = current
            continue

        params[key] = value

    return DTO.fromdict(params)
