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
from pyasn1.type import char
from pyasn1_modules import rfc5280


class Name(pydantic.BaseModel):
    kind: str
    value: Any

    @classmethod
    def parse_value(cls, value: str | char.IA5String) -> Any:
        if isinstance(value, char.IA5String):
            value = str(value)
        return value

    @pydantic.validator('value', pre=True)
    def preprocess_value(cls, value: Any):
        return cls.parse_value(value)

    def encode_value(self) -> Any:
        value = self.value
        if hasattr(self.value, 'asn1'):
            value = value.asn1()
        return value

    def asn1(self) -> rfc5280.GeneralName:
        obj = rfc5280.GeneralName()
        obj[self.kind] = self.encode_value()
        return obj