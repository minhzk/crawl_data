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
"""Declares :class:`KeySpecification`."""
from typing import Any
from typing import Generator

import pydantic

from ckms.core import const
from ckms.lib import dsnparse
from ckms.types import Algorithm
from ckms.types import Decrypter
from ckms.types import Encrypter
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import JSONWebKey
from ckms.types import KeyOperationType
from ckms.types import KeyUseType
from ckms.types import Signer
from ckms.types import Verifier
from .basekeyspecification import BaseKeySpecification
from .certificate import Certificate
from .publickeyspecification import PublicKeySpecification


class KeySpecification(BaseKeySpecification, Decrypter, Encrypter, Signer, Verifier):
    """The base class for all provider key configurations."""
    __module__: str = 'ckms.core.models'
    _presets: dict[str, Any] = {}
    provider: IProvider
    kty: str
    kid: str | None = None
    use: KeyUseType | None
    algorithm: Algorithm = pydantic.Field(default=None, alias='alg')
    allow: set[str] = set()
    curve: str | None = None
    loaded: bool = False
    tags: set[str] = set()
    key_ops: set[KeyOperationType] = set()
    certificate: Certificate | None
    dsn: str | None = None

    class Config(BaseKeySpecification.Config):
        allow_population_by_field_name: bool = True

    @pydantic.root_validator(allow_reuse=True, pre=True)
    def _autodiscover(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get('alg'):
            values['algorithm'] = values['alg']
        cls.autodiscover(
            values['provider'],
            values['provider'].inspector,
            values
        )
        return values

    @classmethod
    def autodiscover(
        cls,
        provider: IProvider,
        inspector: IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        """Hook to override key-specific validations."""
        pass

    @classmethod
    def parse_dsn(
        cls,
        dsn: dsnparse.ParseResult,
        **kwargs: Any
    ) -> dict[str, Any]:
        raise NotImplementedError

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        assert isinstance(self.provider, IProvider)

    async def _load(self) -> 'KeySpecification':
        await self.load()
        if not self.key_ops:
            if self.algorithm in const.DH_ALGORITHMS:
                self.key_ops.add(KeyOperationType.deriveKey)
            if self.algorithm in const.ENCRYPTION_ALGORITHMS:
                self.key_ops.add(KeyOperationType.encrypt)
                if self.is_symmetric():
                    self.key_ops.add(KeyOperationType.decrypt)
            if self.algorithm in const.KEYWRAP_ALGORITHMS:
                self.key_ops.add(KeyOperationType.unwrapKey)
                if self.is_symmetric():
                    self.key_ops.add(KeyOperationType.wrapKey)
            if self.algorithm in const.SIGNING_ALGORITHMS:
                self.key_ops.add(KeyOperationType.sign)
                if self.is_symmetric():
                    self.key_ops.add(KeyOperationType.verify)
        if self.certificate is not None:
            await self.certificate.load()
        return self

    async def load(self) -> 'KeySpecification':
        raise NotImplementedError

    def as_public(self) -> PublicKeySpecification:
        ops: set[KeyOperationType]
        if not self.is_loaded():
            raise RuntimeError("Load the specification first before invoking this method.")
        params: dict[str, Any] = {
            'private': self,
            'provider': 'local',
            'kid': self.kid,
            'kty': self.kty,
            'alg': self.algorithm,
            'use': self.use,
            'crv': self.curve,
            'key': self.get_public_key(),
            'tags': self.tags,
            'certificate': self.certificate
        }
        params['key_ops'] = ops = set()
        if KeyOperationType.decrypt in self.key_ops:
            ops.add(KeyOperationType.encrypt)
        if KeyOperationType.deriveKey in self.key_ops:
            ops.add(KeyOperationType.deriveKey)
        if KeyOperationType.sign in self.key_ops:
            ops.add(KeyOperationType.verify)
        if KeyOperationType.unwrapKey in self.key_ops:
            ops.add(KeyOperationType.wrapKey)
        return PublicKeySpecification(**params)

    def as_jwk(self, private: bool = False) -> JSONWebKey:
        assert isinstance(self.provider, IProvider)
        if self.is_symmetric() and not private: # pragma: no cover
            raise TypeError(
                "Symmetric keys do not have a public key. Set `private=True` "
                "to project the private key to a JSON Web Key (JWK)."
            )
        claims: dict[str, Any] = {}
        if self.certificate:
            claims.update(self.certificate.claims())
        return self.provider.jwk(
            spec=self,
            private=private,
            **claims
        )

    def can_encrypt(self) -> bool:
        return self.can_perform(KeyOperationType.encrypt)

    def can_perform(self, op: str) -> bool:
        is_allowed = op in self.key_ops
        if self.is_asymmetric():
            public = self.as_public()
            is_allowed |= public.can_perform(op)
        return is_allowed

    def can_sign(self) -> bool:
        return self.can_perform(KeyOperationType.sign)

    def can_verify(self) -> bool:
        return self.use == 'sig'

    def can_wrap(self) -> bool:
        is_allowed = KeyOperationType.wrapKey in self.key_ops
        if self.is_asymmetric():
            is_allowed = KeyOperationType.unwrapKey in self.key_ops
        return is_allowed

    def get_key_material(self) -> bytes:
        """Return the key material, if available."""
        raise NotImplementedError

    def get_digest_oid(self) -> str | None:
        return self.algorithm.get_digest_oid()

    def is_aead(self) -> bool:
        return self.algorithm in {
            'A128GCM', 'A192GCM', 'A256GCM',
            'A128GCMKW', 'A192GCMKW', 'A256GCMKW'
        }

    def __await__(self) -> Generator[Any, None, 'KeySpecification']:
        if not self.is_loaded():
            return self._load().__await__()

        # TODO: a very quick and ugly hack.
        async def f():
            return self
        return f().__await__()
