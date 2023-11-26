# Copyright 2022 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# type: ignore
from typing import Any

from ckms.lib import dsnparse
from .keychain import get_default_keychain
from .keychain import Keychain
from .keyinspector import KeyInspector
from .provider import Provider
from .models import RemoteBlobParams as RemoteBlob
from .models import KeySpecification


__all__ = [
   'get_default_keychain',
   'types',
   'KeyInspector',
   'KeySpecification',
   'Provider',
   'RemoteBlob',
]


def parse_dsn(dsn: str | dsnparse.ParseResult) -> dict[str, Any]:
   """Parse a key specification from a Data Source Name (DSN)."""
   if isinstance(dsn, str):
      dsn = dsnparse.parse(dsn)
   p = provider(dsn.scheme)
   return {**p.parse_dsn(dsn), 'dsn': dsn.dsn}


def parse_spec(spec: dict[str, Any]) -> KeySpecification:
    """Parse the specification of a *key* using the parameters defined by the
    specification `spec`.
    """
    p = provider(spec.get('provider'))
    return p.parse_spec(spec)


def provider(name: str) -> Provider:
    """Configure the provider with the given name and return the
    configured instance.
    """
    return Provider.get(name) # type: ignore


async def fetch(spec: RemoteBlob | str, **params: Any) -> bytes:
   """Fetches the content of the remote blob using the parameters
   specified. Return a byte-string holding the content.
   """
   if isinstance(spec, str):
      spec = RemoteBlob(provider=spec, **params)
   provider = Provider.get(spec.provider)
   return await provider.fetch(spec) # type: ignore
