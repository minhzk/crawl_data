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
"""Declares :class:`IProvider`."""
from typing import Any
from typing import TypeAlias
from typing import Union

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import x25519

from .keyoperationtype import KeyOperationType


class IKeyInspector:
    __module__: str = 'cbra.types'

    PublicKeyType: TypeAlias = Union[
        ec.EllipticCurvePublicKey,
        ed448.Ed448PublicKey,
        ed25519.Ed25519PublicKey,
        rsa.RSAPublicKey,
        x448.X448PublicKey,
        x25519.X25519PublicKey
    ]

    PrivateKeyType: TypeAlias = Union[
        ec.EllipticCurvePrivateKey,
        ed448.Ed448PrivateKey,
        ed25519.Ed25519PrivateKey,
        rsa.RSAPrivateKey,
        x448.X448PrivateKey,
        x25519.X25519PrivateKey
    ]

    KeyType: TypeAlias = PublicKeyType | PrivateKeyType

    def calculate_kid(self, key: Any) -> str:
        raise NotImplementedError

    def from_jwk(self, jwk: dict[str, Any]) -> KeyType | bytes:
        raise NotImplementedError

    def get_algorithm_curve(self, algorithm: str) -> str | None:
        raise NotImplementedError

    def get_algorithm_use(self, algorithm: str) -> str:
        raise NotImplementedError

    def get_curve_by_algorithm(self, algorithm: str) -> ec.EllipticCurve:
        raise NotImplementedError

    def get_public_key_ops(self, private: list[KeyOperationType]) -> list[KeyOperationType]:
        raise NotImplementedError

    def to_bytes(self, key: Any) -> bytes:
        raise NotImplementedError

    def to_jwk(
        self,
        key: Any
    ) -> dict[str, Any]:
        """Return a dictionary holding a representation of the key as
        a JSON Web Key (JWK).
        """
        raise NotImplementedError