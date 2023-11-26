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
import functools
from typing import Any

import pydantic
from cryptography.hazmat.primitives.asymmetric.types import PUBLIC_KEY_TYPES
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from pyasn1_modules import rfc5280

from ckms.ext import asn1
from ckms.pkix.oid import ID_EC_PUBLICKEY
from ckms.ext.pkcs.oid import RSA_PKCS1v15
from ckms.ext.rfc5480.types import ECParameters
from .subjectpublickeyalgorithmidentifier import SubjectPublicKeyAlgorithmIdentifier


class SubjectPublicKeyInfo(asn1.ASN1Model):
    __asn1spec__: type[rfc5280.SubjectPublicKeyInfo] = rfc5280.SubjectPublicKeyInfo

    algorithm: SubjectPublicKeyAlgorithmIdentifier

    public_key: asn1.fields.BitString = pydantic.Field(
        default=...,
        alias='subjectPublicKey'
    )

    @classmethod
    def frompublic(cls, key: PUBLIC_KEY_TYPES):
        return cls._frompublic(key)

    @functools.singledispatchmethod
    @classmethod
    def _frompublic(cls, key: PUBLIC_KEY_TYPES) -> 'SubjectPublicKeyInfo':
        raise TypeError(type(key).__name__)

    @_frompublic.register
    @classmethod
    def _fromec(cls, key: ec.EllipticCurvePublicKey) -> Any:
        return cls(
            algorithm=SubjectPublicKeyAlgorithmIdentifier.parse_obj({
                'algorithm': ID_EC_PUBLICKEY,
                'parameters': ECParameters.parse_obj({'namedCurve': key.curve})
            }),
            subjectPublicKey=key.public_bytes( # type: ignore
                encoding=Encoding.X962,
                format=PublicFormat.UncompressedPoint
            )
        )

    @_frompublic.register
    @classmethod
    def _fromrsa(cls, key: rsa.RSAPublicKey) -> Any:
        return cls(
            algorithm=SubjectPublicKeyAlgorithmIdentifier.parse_obj({
                'algorithm': RSA_PKCS1v15,
                'parameters': None
            }),
            subjectPublicKey=key.public_bytes( # type: ignore
                encoding=Encoding.DER,
                format=PublicFormat.PKCS1
            )
        )

    def get_public_key(self) -> PUBLIC_KEY_TYPES:
        if self.algorithm.name not in {ID_EC_PUBLICKEY, RSA_PKCS1v15}:
            raise NotImplementedError(self.algorithm)
        public_key = self.public_key
        load = load_der_public_key
        if isinstance(self.algorithm.parameters, ECParameters):
            assert self.algorithm.parameters is not None
            load = functools.partial(
                ec.EllipticCurvePublicKey.from_encoded_point,
                self.algorithm.parameters.curve.get()
            )
        return load(public_key)