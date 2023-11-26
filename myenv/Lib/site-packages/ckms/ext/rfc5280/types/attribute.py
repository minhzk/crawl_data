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
from pyasn1.codec.der.encoder import encode as encode_der
from pyasn1.type.base import Asn1Type
from pyasn1.type.char import PrintableString
from pyasn1.type.char import UTF8String
from pyasn1_modules import rfc5280

from ckms.ext import asn1


class Attribute(pydantic.BaseModel):
    type: str
    value: Any

    @pydantic.validator('value', pre=True)
    def validate_value(
        cls,
        value: Any
    ) -> Any:
        obj = value
        if isinstance(value, rfc5280.AttributeValue):
            obj = asn1.decode_der(bytes(value))
        elif isinstance(value, Asn1Type):
            raise NotImplementedError(type(value))
        if isinstance(obj, (PrintableString, UTF8String)):
            obj = str(obj)
        return obj

    def asn1(self) -> rfc5280.AttributeTypeAndValue:
        obj = rfc5280.AttributeTypeAndValue()
        obj.setComponentByPosition(0, self.type) # type: ignore
        if not isinstance(self.value, str):
            raise NotImplementedError(type(self.value))
        obj.setComponentByPosition(1, encode_der(self.value, UTF8String())) # type: ignore
        return obj