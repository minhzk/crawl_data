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
"""Declares :class:`Keychain`."""
import asyncio
from collections import OrderedDict
from typing import Iterator, cast
from typing import Any
from typing import Generator

from ckms.types import IKeychain
from ckms.types import IOperationPerformer
from ckms.types import JSONWebKeySet
from .models import KeySpecification
from .models import PublicKeySpecification
from .provider import Provider


class Keychain(IKeychain):
    """An in-memory :class:`~ckms.core.types.IKeychain` implementation."""
    __module__: str = 'ckms.core'
    _keys: OrderedDict[str, IOperationPerformer]

    @classmethod
    def fromdict(cls, keys: dict[str, Any]) -> 'IKeychain':
        keychain = cls() # type: ignore
        keychain.configure(keys)
        return keychain

    def __init__(
        self,
        keys: OrderedDict[str, IOperationPerformer] | None = None
    ):
        self._keys = keys or OrderedDict()

    def add(
        self,
        name: str,
        spec: KeySpecification | PublicKeySpecification | dict[str, Any]
    ) -> KeySpecification | PublicKeySpecification:
        """Add a key to the :class:`Keychain`."""
        if not isinstance(spec, (KeySpecification, PublicKeySpecification)):
            provider = Provider.get(spec.get('provider'))
            spec = cast(KeySpecification, provider.parse_spec(spec))
        if name in self._keys:
            raise ValueError(
                f"Key '{name}' is already registered in the keychain."
            )
        self._keys[name] = spec
        return spec

    def as_jwks(self, private: bool = False) -> JSONWebKeySet:
        """Return a :class:`JSONWebKeySet` instance holding the keys
        in the instance.
        """
        if private:
            raise NotImplementedError
        return JSONWebKeySet(
            keys=[
                spec.as_jwk()
                for spec in self._keys.values()
                if isinstance(spec, PublicKeySpecification)
            ]
        )

    def configure(
        self,
        keys: dict[str, dict[str, Any] | KeySpecification]
    ) -> None:
        """Configure the :class:`Keychain` from a dictionary, where the
        keys represent the names of the keys.
        """
        for name, spec in keys.items():
            self.add(name, spec)

    def dict(self) -> dict[str, Any]: # pragma: no cover
        """Return the keys in the :class:`Keychain` as a dictionary, mapping
        key identifiers to key objects.
        """
        return OrderedDict(self._keys)

    def filter(
        self,
        algorithm: str | None = None,
        kid: str | None = None,
        use: str | None = None,
        op: str | None = None
    ) -> 'IKeychain':
        Impl = type(self)
        if kid is not None and not self.has(kid):
            return Impl(keys=OrderedDict())
        keys: OrderedDict[str, IOperationPerformer] = OrderedDict()
        for name, spec in self._keys.items():
            spec = cast(KeySpecification, spec)
            if not spec.is_loaded():
                raise RuntimeError("Specification is not loaded.")
            assert spec.algorithm is not None
            if algorithm is not None and spec.algorithm != algorithm:
                continue
            if use is not None and spec.use != use:
                continue
            if op is not None and not spec.can_perform(op):
                continue
            keys[name] = spec 
        return Impl(keys=keys)

    def get(self, kid: str | None) -> KeySpecification:
        if not self.has(kid):
            raise KeyError(kid)
        return cast(KeySpecification, self._keys[kid or ''])

    def has(self, kid: str | None) -> bool:
        return kid in self._keys

    def private(self) -> 'IKeychain':
        """Return the :class:`Keychain` with only the keys that can perform
        private operations.
        """
        return type(self)(keys={
            x.kid: x for x in self._keys.values()
            if isinstance(x, KeySpecification)
        })

    def public(self) -> 'IKeychain':
        """Return the :class:`Keychain` with only the keys that can perform
        public operations.
        """
        return type(self)(keys={
            x.kid: x for x in self._keys.values()
            if isinstance(x, PublicKeySpecification)
        })

    def tagged(self, tags: str | list[str] | set[str]) -> 'IKeychain':
        Impl = type(self)
        if isinstance(tags, str):
            tags = {tags}
        if not isinstance(tags, set):
            tags = set(tags)
        keys: OrderedDict[str, IOperationPerformer] = OrderedDict()
        for name, spec in self._keys.items():
            if not bool(spec.tags & tags):
                continue
            if not spec.is_loaded():
                raise RuntimeError(
                    "Keys must be loaded before creating a new instance."
                )
            keys[name] = spec

        return Impl(keys=keys)

    async def _configure(self) -> IKeychain:
        await asyncio.gather(*[self._load_spec(x) for x in self])
        return self

    async def _load_spec(self, spec: KeySpecification) -> KeySpecification:
        if not spec.is_loaded():
            await spec
            assert spec.kid is not None
            if spec.is_asymmetric() and not spec.is_public():
                assert spec.kid is not None
                self._keys[spec.kid] = spec.as_public()
            elif spec.kid not in self._keys:
                self._keys[spec.kid] = spec
        return spec

    def __await__(self) -> Generator[Any, None, IKeychain]:
        return self._configure().__await__()

    def __iter__(self) -> Iterator[KeySpecification]:
        return iter(list(self._keys.values())) # type: ignore

    def __len__(self) -> int:
        return len(self._keys)


default: Keychain = Keychain()


def get_default_keychain() -> Keychain: # pragma: no cover
    """Return the default :class:`Keychain` instance used by the
    application.
    """
    return default
