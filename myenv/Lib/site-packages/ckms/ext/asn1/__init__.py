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
import enum
from typing import cast
from typing import Any

import pydantic
from pyasn1.type.base import Asn1Type
from pyasn1.type import univ
from pyasn1.codec.ber.decoder import decode as _decode_ber
from pyasn1.codec.ber.encoder import encode as _encode_ber
from pyasn1.codec.der.decoder import decode as _decode_der
from pyasn1.codec.der.encoder import encode as _encode_der

from . import fields


__all__: list[str] = [
    'fields',
    'ASN1Model'
]


InvalidBER: Exception = ValueError("Invalid BER encoding.")
InvalidDER: Exception = ValueError("Invalid DER encoding.")


class ObjectIdentifierEnum(enum.Enum):

    def asn1(self) -> univ.ObjectIdentifier:
        return univ.ObjectIdentifier(self.value)


class ASN1Model(pydantic.BaseModel):
    __asn1spec__: type[Asn1Type] | None = None

    @classmethod
    def parse_der(cls, value: bytes) -> 'ASN1Model':
        assert cls.__asn1spec__ is not None
        return cls.parse_obj(decode_der(value, cls.__asn1spec__()))

    def asn1(self) -> Asn1Type:
        assert self.__asn1spec__ is not None
        obj = self.__asn1spec__()
        for field in self.__fields__.values():
            v = getattr(self, field.name)
            if v is None:
                continue
            if hasattr(v, 'asn1'):
                obj[field.alias] = v.asn1() # type: ignore
            elif isinstance(v, Asn1Type):
                obj[field.alias] = v # type: ignore
        #if not obj.isValue: # type: ignore
        #    raise ValueError(
        #        f"The ASN.1 schema created by {type(self).__name__} is not valid."
        #    )
        return obj

    def der(self) -> bytes:
        return _encode_der(self.asn1()) # type: ignore

    class Config:
        arbitrary_types_allowed: bool = True


def decode_ber(
    value: bytes | Asn1Type,
    spec: Asn1Type | None = None
) -> Asn1Type:
    """Decode a BER-encoded datastructure using an optional schema."""
    if isinstance(value, univ.Any):
        value, _ = _decode_ber(bytes(value)) # type: ignore
        if _:
            raise InvalidBER
    if isinstance(value, univ.OctetString):
        value = bytes(value)
    obj, _ = _decode_ber(value, asn1Spec=spec) # type: ignore
    if _:
        raise InvalidBER
    return cast(Asn1Type, obj)


def decode_der(
    value: bytes | univ.OctetString,
    spec: Asn1Type | None = None
) -> Asn1Type:
    """Decode a DER-encoded datastructure using an optional schema."""
    obj, _ = _decode_der(value, asn1Spec=spec) # type: ignore
    if _:
        raise InvalidDER
    return cast(Asn1Type, obj)


def encode_der(
    value: bytes,
    spec: Asn1Type | None = None
) -> bytes:
    """Encode a value to bytes using an optional schema."""
    return _encode_der(value, asn1Spec=spec)


def encode_ber(
    value: Any,
    spec: Asn1Type | None = None
) -> univ.OctetString:
    """Encode a value to bytes using an optional schema."""
    return _encode_ber(value, asn1Spec=spec)