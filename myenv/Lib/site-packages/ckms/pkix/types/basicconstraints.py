from typing import Any
from typing import Literal

import pydantic
from pyasn1.type import univ
from pyasn1_modules import rfc5280

from ckms.ext import asn1
from .basecertificateextension import BaseCertificateExtension


class BasicConstraints(BaseCertificateExtension):
    ext_id: Literal['2.5.29.19'] = pydantic.Field('2.5.29.19', alias='extnID')
    is_ca: bool = pydantic.Field(False, alias='cA')
    path_length: int | None = pydantic.Field(None, alias='pathLenConstraint')

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        if 'extnValue' in values:
            content = asn1.decode_der(
                value=values.pop('extnValue'),
                spec=rfc5280.BasicConstraints()
            )
            values.update(dict(content)) # type: ignore
        return values

    @pydantic.validator('path_length', pre=True)
    def validate_path_length(
        cls,
        value: int | univ.Integer | None
    ) -> int | None:
        if isinstance(value, univ.Integer):
            value = int(value) if value.isValue else None
        return value

    def get_encoded_extension(self) -> univ.OctetString:
        obj = rfc5280.BasicConstraints()
        obj['cA'] = univ.Boolean(self.is_ca)
        if self.path_length is not None:
            obj['pathLenConstraint'] = univ.Integer(self.path_length)
        return asn1.encode_ber(obj)