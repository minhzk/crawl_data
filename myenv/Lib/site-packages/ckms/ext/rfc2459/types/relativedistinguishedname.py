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
from typing import Any

import pydantic
from pyasn1.codec.der import decoder
from pyasn1.type.char import PrintableString
from pyasn1.type.char import UTF8String
from pyasn1_modules import rfc2459


class RelativeDistinguishedName(pydantic.BaseModel):
    common_name: str | None = pydantic.Field(
        default=None,
        alias='2.5.4.3'
    )

    country: str | None = pydantic.Field(
        default=None,
        alias='2.5.4.6'
    )

    organization_name: str | None = pydantic.Field(
        default=None,
        alias='2.5.4.10'
    )

    @classmethod
    def from_attrs(cls, rdn: rfc2459.RelativeDistinguishedName) -> 'RelativeDistinguishedName':
        attrs: dict[str, str] = {}
        for attr in rdn: # type: ignore
            attrs[str(attr['type'])] = attr['value'] # type: ignore
        return cls.parse_obj(attrs)

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        for oid, value in list(values.items()):
            if not isinstance(value, rfc2459.AttributeValue):
                continue
            obj, _ = decoder.decode(value) # type: ignore
            if _:
                raise ValueError("Invalid DER encoding.")
            if isinstance(obj, (PrintableString, UTF8String)):
                values[oid] = str(obj)
            else:
                raise NotImplementedError(type(obj)) # type: ignore

        return values