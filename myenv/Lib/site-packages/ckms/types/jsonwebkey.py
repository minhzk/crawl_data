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
import enum
import functools
import pathlib
from typing import Any

import pydantic
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.types import PUBLIC_KEY_TYPES
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from ckms.utils import b64decode
from .algorithm import Algorithm
from .encrypter import Encrypter
from .iprovider import IProvider
from .ikeyinspector import IKeyInspector
from .ikeyspecification import IKeySpecification
from .keyoperationtype import KeyOperationType
from .keyusetype import KeyUseType
from .signer import Signer
from .verifier import Verifier


class JSONWebKey(Encrypter, Verifier, Signer, pydantic.BaseModel, IKeySpecification):
    __module__: str = 'ckms.types'

    @property # type: ignore pragma: no cover
    def algorithm(self) -> str | None:
        return self.alg

    @property
    def inspector(self) -> IKeyInspector:
        return self.provider.inspector # type: ignore

    @property # type: ignore
    def provider(self) -> IProvider:
        return IProvider.get('local')

    kty: str | None
    kid: str | None
    alg: Algorithm | None
    crv: str | None
    use: KeyUseType | None # type: ignore
    key_ops: list[KeyOperationType] = []
    x5u: str | None
    x5c: list[str] | None
    x5t: str | None
    x5t_sha256: str | None = pydantic.Field(
        default=None,
        alias="x5t#S256"
    )

    # Key material
    d: str | None
    e: str | None
    n: str | None
    k: str | None
    p: str | None
    q: str | None
    x: str | None
    y: str | None
    dp: str | None
    dq: str | None
    qi: str | None

    @classmethod
    def fromcertificate(cls, *, alg: str, crt: x509.Certificate, **claims: Any) -> 'JSONWebKey':
        """Create a new :class:`JSONWebKey` from a :class:`cryptography.x509.Certificate`
        instance.
        """
        p = IProvider.get('local')
        return cls.parse_obj({
            **p.inspector.to_jwk(crt.public_key()),
            **claims,
            'alg': alg,
            # TODO: Discover key ops from certificate extensions
            'key_ops': {'verify', 'encrypt', 'wrapKey'}
        })

    @classmethod
    def fromfile(cls, filepath: str | pathlib.Path, **claims: Any) -> 'JSONWebKey':
        """Create a new :class:`JSONWebKey` from a PEM-encoded key or
        X.509 certificate at the given `filepath`.
        """
        with open(filepath, 'rb') as f:
            pem = f.read()
            if b'-----BEGIN CERTIFICATE-----' in pem:
                return cls.fromcertificate(
                    crt=x509.load_pem_x509_certificate(pem),
                    **claims
                )
            else:
                return cls.frompem(pem=pem, **claims)

    @classmethod
    def frompem(
        cls,
        pem: bytes,
        *,
        alg: str | None = None,
        use: str | KeyUseType | None = None,
        key_ops: list[str] | list[KeyOperationType] | None = None,
        password: bytes | str | None = None,
        public: bool = False,
        **claims: Any
    ) -> 'JSONWebKey':
        """Create a new :class:`JSONWebKey` instance from a PEM-encoded
        key.
        """
        p = IProvider.get('local')
        f = load_pem_public_key
        if b'PRIVATE KEY-----' in pem:
            if isinstance(password, str): # pragma: no cover
                password = str.encode(password)
            f = functools.partial(load_pem_private_key, password=password)
        jwk = cls.parse_obj({
            'alg': alg,
            'use': use,
            **p.inspector.to_jwk(f(pem)),
            **claims,
            'key_ops': key_ops or [],
        })
        if public and jwk.is_asymmetric():
            jwk = jwk.as_public()
        return jwk

    @classmethod
    def frompublic(cls, key: PUBLIC_KEY_TYPES, **claims: Any) -> 'JSONWebKey':
        p = IProvider.get('local')
        return cls.frompem(p.inspector.to_bytes(key), **claims)

    @pydantic.root_validator(allow_reuse=True, pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        kty = values.get('kty')
        if kty in {'EC', 'OKP'} and not values.get('crv'): # pragma: no cover
            raise ValueError(
                "The 'crv' parameter is required for keys of type "
                "EC or OKP."
            )
        alg = values.get('alg')
        if isinstance(alg, enum.Enum):
            alg = alg.value
        if alg is not None and not isinstance(alg, Algorithm):
            alg = Algorithm.get(alg)
        if alg is not None:
            values['alg'] = alg
            values['use'] = alg.use
        if not values.get('alg') and not values.get('use'):
            raise TypeError("Provide either the 'alg' or 'use' parameter.")
        return values

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.kid is None:
            if self.is_asymmetric():
                self.kid = self.inspector.calculate_kid(self.get_public_key())
            elif self.k:
                self.kid = self.inspector.calculate_kid(b64decode(self.k))
        if self.alg is not None and not self.key_ops:
            self.key_ops = [
                getattr(KeyOperationType, op)
                for op in self.alg.get_key_ops(self.is_public())
            ]

    def as_public(self) -> 'JSONWebKey':
        if not self.is_public():
            key = self.inspector.from_jwk(jwk=self.dict())
            self = JSONWebKey.parse_obj({
                **self.inspector.to_jwk(key.public_key()), # type: ignore
                'kid': self.kid,
                'alg': self.alg,
                'use': self.use,
                'key_ops': self.inspector.get_public_key_ops(self.key_ops),
                'x5u': self.x5u,
                'x5c': self.x5c,
                'x5t': self.x5t,
                'x5t#S256': self.x5t_sha256
            })
        return self

    def can_encrypt(self) -> bool:
        return bool(set(self.key_ops) & {'encrypt', KeyOperationType.encrypt})

    def can_perform(self, op: KeyOperationType | str) -> bool: # pragma: no cover
        return op in self.key_ops

    def can_verify(self) -> bool:
        return KeyOperationType.verify in self.key_ops

    def dict(self, **kwargs: Any) -> dict[str, Any]: # type: ignore pragma: no cover
        kwargs.setdefault('exclude_defaults', True)
        return super().dict(**kwargs)

    def get_public_key(self) -> Any:
        if not self.is_public():
            self = self.as_public()
        return self.inspector.from_jwk(
            jwk=self.dict(exclude_none=True)
        )

    def is_asymmetric(self) -> bool:
        return self.kty in {'EC', 'OKP', 'RSA'}

    def is_loaded(self) -> bool:
        return True

    def is_public(self) -> bool:
        return all([
            getattr(self, attname) is None
            for attname in ['d', 'k', 'p', 'q', 'dp', 'dq', 'qi']
        ])

    def json(self, **kwargs: Any) -> str: # type: ignore pragma: no cover
        kwargs.setdefault('exclude_defaults', True)
        return super().json(**kwargs)
