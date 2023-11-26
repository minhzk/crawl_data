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
import ipaddress
from typing import Any

import pydantic
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric.types import PUBLIC_KEY_TYPES
from pyasn1.codec.der import encoder
from pyasn1_modules import rfc2986

from ckms.ext import asn1
from ckms.ext.rfc5280.types import SignatureDigestAlgorithmIdentifier
from ckms.types import JSONWebKey
from ckms.types import Signer
from .certificationrequestinfo import CertificationRequestInfo
from .dnsname import DNSName
from .ipaddressname import IPAddressName
from .uriname import URIName


class CertificationRequest(asn1.ASN1Model):
    __asn1spec__: type[rfc2986.CertificationRequest] = rfc2986.CertificationRequest

    signed_data: bytes = b''

    info: CertificationRequestInfo = pydantic.Field(
        default_factory=CertificationRequestInfo,
        alias='certificationRequestInfo'
    )

    digest_algorithm: SignatureDigestAlgorithmIdentifier | None = pydantic.Field(
        default=None,
        alias='signatureAlgorithm'
    )

    signature: asn1.fields.BitString = asn1.fields.BitString(None)

    @property
    def public_key(self) -> JSONWebKey:
        assert self.digest_algorithm is not None
        return JSONWebKey.frompublic(
            key=self.get_public_key(),
            alg=self.digest_algorithm.get_qualname(
                key=self.info.subject_public_key
            )
        )

    @classmethod
    def new(
        cls,
        public_key: PUBLIC_KEY_TYPES,
    ) -> 'CertificationRequest':
        """Instantiate a new :class:`CertificationRequest` instance. Set the
        `SubjectPublicKeyInfo` attribute and return the new instance.

        The `public_key` parameter is the public key of the signer. The caller
        must ensure that the actual signature is created using the corresponding
        private key.
        """
        return cls(
            certificationRequestInfo=CertificationRequestInfo.new(key=public_key)
        )

    @classmethod
    def parse_der(cls, value: bytes) -> 'CertificationRequest':
        return super().parse_der(value) # type: ignore

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        info = values.get('certificationRequestInfo')
        sig = values.get('signature')
        if info and sig:
            values['signed_data'] = encoder.encode(info)
        return values

    def asn1(self) -> rfc2986.CertificationRequest:
        obj = super().asn1()

        # If there was previously signed data (for example, when this
        # instance was parsed from an existing CSR), use that instead
        # of encoding from this child models.
        if self.signed_data:
            obj.setComponentByName( # type: ignore
                name='certificationRequestInfo',
                value=asn1.decode_der(
                    value=self.signed_data,
                    spec=rfc2986.CertificationRequestInfo()
                )
            )
        return obj # type: ignore

    def add_domain(self, value: str) -> None:
        """Add a domain name to the Subject Alternative Name (SAN)
        certificate extension.
        """
        self.info.extensions.add_san(DNSName(value=value))

    def add_ip(self, value: ipaddress.IPv4Address | str) -> None:
        """Add an IPv4 address to the Subject Alternative Name (SAN)
        certificate extension.
        """
        if isinstance(value, str):
            value = ipaddress.IPv4Address(value)
        self.info.extensions.add_san(IPAddressName(value=value))

    def add_uri(self, value: str) -> None:
        """Add an Uniform Resource Identifier (URI) to the Subject Alternative
        Name (SAN) certificate extension.
        """
        self.info.extensions.add_san(URIName(value=value))

    def can_sign(self, value: bool | None = None) -> bool:
        """Return a boolean indicating if the extension allows the
        verification of digital signatures.
        """
        return self.info.extensions.can_sign(value)

    def get_public_key(self) -> PUBLIC_KEY_TYPES:
        """Return the public key of the signer."""
        return self.info.subject_public_key.get_public_key()

    def nonrepudiable(self, value: bool | None = None) -> bool:
        """Return a boolean indicating if signatures made by the private
        key associated to the certificate public key are nonrepudiable.
        """
        return self.info.extensions.nonrepudiable(value)

    def pem(self) -> bytes:
        """Return a byte-sequence holding the PEM-encoded CSR."""
        csr = x509.load_der_x509_csr(self.der())
        return csr.public_bytes(Encoding.PEM)

    def verify(self, key: JSONWebKey | None = None) -> bool:
        """Verify that the signature was made using the included public
        key.
        """
        key = key or self.public_key
        if self.digest_algorithm is None:
            return False
        return key.verify(
            signature=self.info.subject_public_key.algorithm.normalize_signature(self.signature),
            message=self.signed_data
        )

    async def sign(self, signer: Signer) -> None:
        """Sign the :class:`CertificationRequest` with the provided `signer`."""
        if self.signed_data:
            raise ValueError("The CertificationRequest already has a signature")
        self.signed_data = self.info.der()
        self.digest_algorithm = SignatureDigestAlgorithmIdentifier.parse_obj({
            'algorithm': signer.get_digest_oid()
        })
        self.signature = asn1.fields.BitString(
            self.info.subject_public_key.algorithm.encode_signature(await signer.sign(self.signed_data))
        )