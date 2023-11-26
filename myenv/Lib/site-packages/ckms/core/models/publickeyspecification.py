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
"""Declares :class:`PublicKeySpecification`."""
from typing import Any, Awaitable
from typing import Generator
from ckms.types.decrypter import Decrypter

import pydantic

from ckms.types import CryptographyPublicKeyType
from ckms.types import KeyAlgorithmType
from ckms.types import KeyOperationType
from ckms.types import KeyUseType
from ckms.types import Encrypter
from ckms.types import EdwardsCurveType
from ckms.types import EllipticCurveType
from ckms.types import IKeySpecification
from ckms.types import IProvider
from ckms.types import Signer
from ckms.types import Verifier
from .certificate import Certificate


class PublicKeySpecification(IKeySpecification, Encrypter, Verifier, pydantic.BaseModel):
    private: Decrypter | Signer | None = None
    provider: IProvider
    kid: str
    kty: str
    alg: KeyAlgorithmType
    crv: EdwardsCurveType | EllipticCurveType | None = None
    use: KeyUseType
    key_ops: set[KeyOperationType]
    tags: set[str] = set()
    key: CryptographyPublicKeyType
    certificate: Certificate | None

    @property # type: ignore
    def algorithm(self) -> str:
        return self.alg

    def as_jwk(self, private: bool = False) -> dict[str, Any]:
        assert not private
        claims: dict[str, Any] = {
            **self.provider.inspector.to_jwk(self.key),
            'alg': self.alg,
            'crv': self.crv,
            'use': self.use,
            'key_ops': self.key_ops
        }
        if self.certificate:
            claims.update(self.certificate.claims())
        return claims

    def can_sign(self) -> bool:
        return False

    def can_wrap(self) -> bool:
        """Return a boolean indicating if the key can wrap another key."""
        return KeyOperationType.wrapKey in self.key_ops

    def can_perform(self, op: str) -> bool:
        """Return a boolean indicating if the key can perform the
        given cryptographic operation.
        """
        return op in self.key_ops

    def can_verify(self) -> bool:
        """Return a boolean indicating if this implementation can verify
        a digital signature.
        """
        return self.use == 'sig'

    def decrypt(self, *args: Any, **kwargs: Any) -> bytes | Awaitable[bytes]:
        if self.private is None:
            raise ValueError(f"Private key not available for public key {self.kid}")
        assert isinstance(self.private, Decrypter)
        return self.private.decrypt(*args, **kwargs)

    def get_public_key(self) -> CryptographyPublicKeyType:
        """Return the public key that may be used for encryption or
        verifcation.
        """
        return self.key

    def is_aead(self) -> bool:
        """Return a boolean indicating if the operator supports Authenticated
        Encryption with Associated Data (AEAD).
        """
        return False

    def is_asymmetric(self) -> bool:
        """Return a boolean indicating if the key is an asymmetric
        algorithm.
        """
        return True

    def is_loaded(self) -> bool: 
        """Return a boolean indicating if the metadata describing the
        key is retrieved.
        """
        return True

    def is_public(self) -> bool:
        """Return a boolean indicating if this specification represent
        a public key.
        """
        return True

    def is_symmetric(self) -> bool:
        """Return a boolean indicating if the key is a symmetric
        algorithm.
        """
        return False

    def __await__(self) -> Generator[None, Any, 'PublicKeySpecification']:
        async def f(): return self
        return f().__await__()

    class Config:
        arbitrary_types_allowed: bool = True
