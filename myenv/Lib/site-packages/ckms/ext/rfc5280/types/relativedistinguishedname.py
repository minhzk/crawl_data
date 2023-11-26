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
from typing import Optional

from pyasn1_modules import rfc5280

from .attribute import Attribute


class RelativeDistinguishedName(list[Attribute]):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: list[Attribute] | rfc5280.RelativeDistinguishedName | None
    ) -> Optional['RelativeDistinguishedName']:
        if value is None:
            return None
        if isinstance(value, rfc5280.RelativeDistinguishedName):
            value = [
                Attribute.parse_obj({'type': str(x[0]), 'value': x[1]}) # type: ignore
                for x in value # type: ignore
            ]
        assert isinstance(value, list)
        return cls(value)

    def asn1(self) -> rfc5280.RelativeDistinguishedName:
        obj = rfc5280.RelativeDistinguishedName()
        for attr in self:
            obj.append(attr.asn1()) # type: ignore
        return obj