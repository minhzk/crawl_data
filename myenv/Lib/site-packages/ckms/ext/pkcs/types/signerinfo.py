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
import pydantic
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder
from pyasn1.type import univ
from pyasn1_modules import rfc2315

from ckms.ext.x509.types import AlgorithmIdentifier
from .attribute import Attribute
from .issuerandserialnumber import IssuerAndSerialNumber


class SignerInfo(pydantic.BaseModel):
    version: int

    issuer: IssuerAndSerialNumber = pydantic.Field(
        default=...,
        alias='issuerAndSerialNumber'
    )

    digest_algorithm: AlgorithmIdentifier = pydantic.Field(
        default=...,
        alias='digestAlgorithm'
    )

    authenticated_attrs: list[rfc2315.Attribute] | None = pydantic.Field(
        default=None,
        alias='authenticatedAttributes'
    )

    encryption_algorithm: str = pydantic.Field(
        default=...,
        alias='digestEncryptionAlgorithm'
    )

    signature: bytes = pydantic.Field(
        default=...,
        alias='encryptedDigest'
    )

    unauthenticated_attrs: list[Attribute] | None = pydantic.Field(
        default=None,
        alias='unauthenticatedAttributes'
    )

    @pydantic.validator('digest_algorithm', pre=True)
    def validate_digest_algorithm(
        cls,
        value: rfc2315.DigestAlgorithmIdentifier | str | AlgorithmIdentifier
    ) -> str | AlgorithmIdentifier:
        if isinstance(value, rfc2315.DigestAlgorithmIdentifier):
            value = str(value['algorithm']) # type: ignore
        return value


    @pydantic.validator('encryption_algorithm', pre=True)
    def validate_encryption_algorithm(
        cls,
        value: rfc2315.DigestEncryptionAlgorithmIdentifier | str
    ) -> str:
        if isinstance(value, rfc2315.DigestEncryptionAlgorithmIdentifier):
            value = str(value['algorithm']) # type: ignore
        return value

    @pydantic.validator('signature', pre=True)
    def validate_signature(
        cls,
        value: bytes | rfc2315.EncryptedDigest
    ) -> bytes:
        if isinstance(value, rfc2315.EncryptedDigest):
            value = bytes(value)
        return value

    @pydantic.validator('authenticated_attrs', pre=True)
    def validate_authenticated_attrs(
        cls,
        value: list[rfc2315.Attribute] | rfc2315.Attributes | None
    ) -> list[rfc2315.Attribute] | None:
        if isinstance(value, rfc2315.Attributes):
            value = list(value)
        return value

    @pydantic.validator('unauthenticated_attrs', pre=True)
    def validate_unauthenticated_attrs(
        cls,
        value: list[rfc2315.Attribute] | rfc2315.Attributes | None
    ) -> list[rfc2315.Attribute] | None:
        if isinstance(value, rfc2315.Attributes):
            value = list(value)
        return value

    @property
    def signed_data(self) -> bytes:
        """The digest that was signed by the signer."""
        obj = univ.SetOf()
        for i, attr in enumerate(self.authenticated_attrs or []):
            obj.setComponentByPosition(i, attr) # type: ignore
        return self.get_digest(encoder.encode(obj)) # type: ignore

    @property
    def signed_digest(self) -> bytes:
        """The digest of the signed data."""
        digest: bytes
        for attr in (self.authenticated_attrs or []):
            t = attr[0]
            v = attr[1]
            if str(t) != '1.2.840.113549.1.9.4':
                continue
            digest, _ = decoder.decode( # type: ignore
                bytes(v[0]),
                asn1Spec=univ.OctetString()
            )
            if _:
                raise ValueError("Invalid DER encoding.")
            break
        else:
            raise ValueError("No digest present in SignerInfo.")
        return bytes(digest)

    def get_digest(self, data: bytes) -> bytes:
        """Return a byte-string containing a digest of `data` using the
        hashing algorithm specified by the signer.
        """
        return self.digest_algorithm.digest(data)

    def verify(
        self,
        key: ec.EllipticCurvePublicKey | rsa.RSAPublicKey,
        data: bytes
    ) -> bool:
        return False

    class Config:
        arbitrary_types_allowed: bool = True