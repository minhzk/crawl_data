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
"""Declares :class:`JSONWebKeySet`."""
from typing import Any, Iterable

import pydantic

from .ikeychain import IKeychain
from .jsonwebkey import JSONWebKey


class JSONWebKeySet(pydantic.BaseModel, IKeychain):
    __module__: str = 'ckms.types'
    keys: list[JSONWebKey] = []
    _index: dict[str, int] = pydantic.PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._index = {}
        for i, spec in enumerate(self.keys):
            if not spec.kid: # pragma: no cover
                continue
            self._index[spec.kid] = i

    def as_list(self) -> list[JSONWebKey]:
        """Return the keys in the JWKS as a list."""
        return self.keys

    def dict(self, **kwargs: Any) -> dict[str, Any]: # type: ignore pragma: no cover
        kwargs.setdefault('exclude_defaults', True)
        return super().dict(**kwargs)

    def filter( # type: ignore
        self,
        algorithm: str | None = None,
        kid: str | None = None,
        use: str | None = None,
        op: str | None = None
    ) -> 'JSONWebKeySet':
        return type(self)(keys=super().filter(algorithm, kid, use, op, self.keys))

    def get(self, kid: str | None) -> JSONWebKey:
        if not self.has(kid):
            raise KeyError(kid)
        assert kid is not None
        return self.keys[self._index[kid]]

    def get_encryption_algorithms(self) -> list[str]:
        return [x.alg for x in self.keys if (x.use == 'enc' and x.alg)]

    def get_encryption_keys(self) -> list[JSONWebKey]:
        return [x for x in self.keys if x.use == 'enc']

    def get_signing_algorithms(self) -> list[str]:
        return [x.alg for x in self.keys if (x.use == 'sig' and x.alg)]

    def get_signing_keys(self) -> list[JSONWebKey]:
        return [x for x in self.keys if x.use == 'sig']

    def json(self, **kwargs: Any) -> str: # type: ignore pragma: no cover
        kwargs.setdefault('exclude_defaults', True)
        return super().json(**kwargs)

    def has(self, kid: str | None) -> bool:
        return kid in self._index

    def __len__(self) -> int:
        return len(self.keys)

    def __iter__(self) -> Iterable[JSONWebKey]: # type: ignore
        return iter(self.keys)