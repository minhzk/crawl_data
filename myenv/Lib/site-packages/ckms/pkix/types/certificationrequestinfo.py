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
from typing import Any

import pydantic
from cryptography.hazmat.primitives.asymmetric.types import PUBLIC_KEY_TYPES
from pyasn1_modules import rfc2986

from ckms.ext import asn1
from ckms.ext.rfc5280.types import RDNSequence
from ckms.ext.rfc5280.types import SubjectPublicKeyInfo
from ..oid import ID_EXTENSION_REQUEST
from .attributelist import AttributeList
from .certificateextensionsequence import CertificateExtensionSequence


class CertificationRequestInfo(asn1.ASN1Model):
    __asn1spec__: type[rfc2986.CertificationRequestInfo] = rfc2986.CertificationRequestInfo
    version: asn1.fields.Integer = asn1.fields.Integer(0)
    subject: RDNSequence = RDNSequence()
    subject_public_key: SubjectPublicKeyInfo = pydantic.Field(
        default=...,
        alias='subjectPKInfo'
    )
    attributes: AttributeList = AttributeList()
    _extensions: CertificateExtensionSequence = pydantic.PrivateAttr(
        default=CertificateExtensionSequence([])
    )

    @property
    def extensions(self) -> CertificateExtensionSequence:
        return self._extensions

    @classmethod
    def new(cls, key: PUBLIC_KEY_TYPES) -> 'CertificationRequestInfo':
        return cls(
            subjectPKInfo=SubjectPublicKeyInfo.frompublic(key)
        )

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if self.attributes.has(ID_EXTENSION_REQUEST):
            self._extensions = CertificateExtensionSequence.from_attribute(
                attribute=self.attributes.get(ID_EXTENSION_REQUEST)
            )

    def asn1(self) -> asn1.Asn1Type:
        self.attributes.add(self._extensions.as_attribute())
        return super().asn1()