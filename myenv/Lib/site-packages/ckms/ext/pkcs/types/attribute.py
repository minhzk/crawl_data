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
from pyasn1_modules import rfc2459


class Attribute(pydantic.BaseModel):
    type: str
    values: list[Any]

    @pydantic.validator('type', pre=True)
    def validate_type(cls, value: str | rfc2459.AttributeType) -> str:
        if isinstance(value, rfc2459.AttributeType):
            value = str(value)
        return value

    @pydantic.validator('values', pre=True)
    def validate_value(cls, value: rfc2459.AttributeValue) -> list[Any]:
        return list(value)