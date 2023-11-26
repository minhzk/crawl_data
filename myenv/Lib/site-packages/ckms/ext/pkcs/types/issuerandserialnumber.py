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
import pydantic
from pyasn1_modules import rfc2315

from ckms.ext.rfc2459.types import RelativeDistinguishedName


class IssuerAndSerialNumber(pydantic.BaseModel):
    name: list[RelativeDistinguishedName] = pydantic.Field(..., alias='issuer')
    serial_number: int = pydantic.Field(..., alias='serialNumber')

    @pydantic.validator('name', pre=True)
    def validate_name(
        cls,
        value: rfc2315.Name | RelativeDistinguishedName
    ) -> list[RelativeDistinguishedName]:
        names: list[RelativeDistinguishedName] = []
        if isinstance(value, rfc2315.Name):
            for rdn in value[0]: # type: ignore
                names.append(
                    RelativeDistinguishedName.from_attrs(rdn) # type: ignore
                )
            value = names # type: ignore
        assert isinstance(value, list)
        return value