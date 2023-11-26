# Copyright 2018 Cochise Ruhulessin
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
from ckms.types import JSONWebKeySet
from .types import BaseIssuerCache


JWKS_CACHE: dict[str, JSONWebKeySet] = {}


class MemoryIssuerCache(BaseIssuerCache):
    """A :class:`~ckms.jose.types.BaseIssuerCache` implementation
    that retains the keys in local memory.
    """
    __module__: str = 'ckms.jose'

    async def get(self, issuer: str) -> JSONWebKeySet | None:
        return JWKS_CACHE.get(issuer)

    async def add(self, issuer: str, jwks: JSONWebKeySet) -> None:
        JWKS_CACHE[issuer] = jwks