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
from typing import cast
from typing import Any
from typing import Sequence

from pyasn1.type import univ
from pyasn1_modules import rfc5280

from ckms.ext import asn1
from ..oid import ID_CE_BASICCONSTRAINTS
from ..oid import ID_CE_KEYUSAGE
from ..oid import ID_CE_SUBJECTALTNAME
from ..oid import ID_EXTENSION_REQUEST
from .attribute import Attribute
from .certificateextension import BaseCertificateExtension
from .certificateextension import BasicConstraints
from .certificateextension import CertificateExtension
from .certificateextension import KeyUsage
from .certificateextension import SubjectAltNames
from .name import Name


class CertificateExtensionSequence(list[BaseCertificateExtension]):
    _index: dict[str, int]

    @property
    def basic_constraints(self) -> BasicConstraints:
        return cast(BasicConstraints, self.get(ID_CE_BASICCONSTRAINTS))

    @property
    def key_usage(self) -> KeyUsage:
        return cast(KeyUsage, self.get(ID_CE_KEYUSAGE))

    @property
    def subject_altnames(self) -> SubjectAltNames | None:
        return cast(SubjectAltNames, self.get(ID_CE_SUBJECTALTNAME))

    @classmethod
    def from_attribute(
        cls,
        attribute: Attribute
    ) -> 'CertificateExtensionSequence':
        extensions = cls([])
        obj, *_ = attribute.decode(rfc5280.Extensions())
        if _:
            raise ValueError("Unexpected length for Extensions.")
        for value in obj: # type: ignore
            ext = CertificateExtension.parse_obj({
                **value,
                'extnID': str(value[0]) # type: ignore
            })
            extensions.add(ext)
        return extensions

    def __init__(
        self,
        extensions: Sequence[BaseCertificateExtension],
        *args: Any,
        **kwargs: Any
    ):
        self._index = {}
        super().__init__(extensions, *args, **kwargs)
        for i, ext in enumerate(self):
            self._index[str(ext.ext_id)] = i
        if ID_CE_BASICCONSTRAINTS not in self._index:
            self.add(BasicConstraints.parse_obj({}))

    def add_san(self, san: Name) -> None:
        """A the given :class:`~ckms.ext.pkix.types.Name` to the Subject
        Alternative Name (SAN) extension.
        """
        if not self.subject_altnames:
            self.add(SubjectAltNames.parse_obj({}))
        assert self.subject_altnames is not None
        if san in self.subject_altnames.names:
            raise ValueError(
                f"Name {san} already in the Subject Alternative Name (SAN)"
            )
        self.subject_altnames.names.append(san)

    def as_attribute(self) -> Attribute:
        ext = rfc5280.Extensions()
        ext.extend([x.asn1() for x in self]) # type: ignore
        values = univ.SetOf()
        values.extend([ # type: ignore
            rfc5280.AttributeValue(asn1.encode_der(ext)) # type: ignore
        ])
        return Attribute(
            type=asn1.fields.ObjectIdentifier(ID_EXTENSION_REQUEST),
            values=values
        )

    def add(self, ext: BaseCertificateExtension) -> None:
        if str(ext.ext_id) in self._index:
            i = self._index[ext.ext_id]
            f = functools.partial(self.__setitem__, i)
        else:
            f = self.append
            i = len(self)
            self._index[ext.ext_id] = i
        return f(ext)

    def can_sign(self, value: bool | None = None) -> bool:
        """Return a boolean indicating if the extension allows the
        verification of digital signatures.
        """
        return self._keyusage(0, value)

    def get(self, oid: str) -> BaseCertificateExtension | None:
        attr: BaseCertificateExtension | None = None
        if oid in self._index:
            attr = self[self._index[oid]] # type: ignore
        return attr

    def nonrepudiable(self, value: bool | None = None) -> bool:
        """Return a boolean indicating if signatures made by the private
        key associated to the certificate public key are nonrepudiable.
        """
        return self._keyusage(1, value)

    def _keyusage(self, use: int, value: bool | None) -> bool:
        if value is not None and not self.key_usage:
            self.add(KeyUsage())
        assert self.key_usage is not None
        if value is not None:
            self.key_usage.set(use, int(value))
        return self.key_usage.get(use)