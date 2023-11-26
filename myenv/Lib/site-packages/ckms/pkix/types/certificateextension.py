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
from typing import cast
from typing import Any
from typing import Literal
from typing import Sequence

import pydantic
from pyasn1.type import univ
from pyasn1_modules import rfc5280
from typing_extensions import Annotated

from ckms.ext import asn1
from .basecertificateextension import BaseCertificateExtension
from .basicconstraints import BasicConstraints
from .extendedkeyusagetype import ExtendedKeyUsageType
from .generalname import Name
from .generalname import GeneralName


class SubjectAltNames(BaseCertificateExtension):
    ext_id: Literal['2.5.29.17'] = pydantic.Field('2.5.29.17', alias='extnID')
    names: list[Name] = []

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ):
        obj = values.pop('extnValue', None)
        names: list[Any] = values.setdefault('names', [])
        if obj is not None:
            value = cast(
                list[rfc5280.GeneralNames],
                asn1.decode_ber(obj, rfc5280.SubjectAltName())
            )
            for altname in value:
                name = cast(str, altname.getName()) # type: ignore
                value = altname.getComponentByName(name) # type: ignore
                names.append(GeneralName.parse_obj({'kind': name, 'value': value}))
        return values

    def get_encoded_extension(self) -> univ.OctetString:
        names = rfc5280.GeneralNames()
        names.extend([x.asn1() for x in self.names]) # type: ignore
        return asn1.encode_ber(names, rfc5280.SubjectAltName())


class KeyUsage(BaseCertificateExtension):
    ext_id: Literal['2.5.29.15'] = pydantic.Field(default='2.5.29.15', alias='extnID')
    mask: rfc5280.KeyUsage = rfc5280.KeyUsage.fromOctetString(b'\x00') # type: ignore

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        if values.get('extnValue'):
            values =  {
                **values,
                'mask': asn1.decode_der(
                    value=values.pop('extnValue'),
                    spec=rfc5280.KeyUsage()
                )
            }
        return values

    def get(self, index: int) -> bool:
        """Get the specified bit on the :class:`~pyasn1_modules.rfc5280.KeyUsage()`
        instance.
        """
        mask: Sequence[int] = cast(Sequence[int], tuple(self.mask))
        return (len(mask) + 1) >= index and bool(mask[index])

    def get_encoded_extension(self) -> univ.OctetString:
        return asn1.encode_ber(self.mask, rfc5280.KeyUsage())

    def set(self, index: int, value: int) -> None:
        """Set the specified bit on the :class:`~pyasn1_modules.rfc5280.KeyUsage()`
        instance.
        """
        mask: list[int] = list(tuple(self.mask)) # type: ignore
        mask[index] = value
        self.mask = rfc5280.KeyUsage(tuple(mask))

    class Config:
        arbitrary_types_allowed: bool = True


class ExtendedKeyUsage(BaseCertificateExtension):
    ext_id: Literal['2.5.29.37'] = pydantic.Field('2.5.29.37', alias='extnID')
    uses: list[ExtendedKeyUsageType] = pydantic.Field(..., alias='extnValue')

    @pydantic.validator('uses', pre=True)
    def preprocess_uses(
        cls,
        value: list[str] | univ.OctetString
    ) -> list[str]:
        if isinstance(value, univ.OctetString):
            content = asn1.decode_der(
                value=value,
                spec=rfc5280.ExtKeyUsageSyntax()
            )
            value = [str(x) for x in content] # type: ignore
        return value

    def get_encoded_extension(self) -> univ.OctetString:
        obj = rfc5280.ExtKeyUsageSyntax()
        obj.extend([rfc5280.KeyPurposeId(x.value) for x in self.uses]) # type: ignore
        return asn1.encode_ber(obj)


class CertificateExtension(pydantic.BaseModel):
    __root__: Annotated[
        BasicConstraints |
        SubjectAltNames |
        KeyUsage |
        ExtendedKeyUsage,
        pydantic.Field(discriminator='ext_id')
    ]

    @classmethod
    def parse_obj(cls, obj: Any) -> BaseCertificateExtension:
        return super().parse_obj(obj).__root__