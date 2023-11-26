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
from pyasn1.type import univ
from pyasn1_modules import rfc5280

from ckms.ext.x509.types import AlgorithmIdentifier


class MessageImprint(pydantic.BaseModel):
    algorithm: AlgorithmIdentifier = pydantic.Field(..., alias='hashAlgorithm')
    message: bytes = pydantic.Field(..., alias='hashedMessage')

    @pydantic.validator('algorithm', pre=True)
    def validate_algorithm(
        cls,
        value: rfc5280.AlgorithmIdentifier | str | AlgorithmIdentifier
    ) -> str | AlgorithmIdentifier:
        if isinstance(value, rfc5280.AlgorithmIdentifier):
            value = str(value['algorithm']) # type: ignore
        return value

    @pydantic.validator('message', pre=True)
    def validate_message(cls, value: bytes | univ.OctetString) -> bytes:
        return bytes(value)