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
# type: ignore
from typing import Any

import pydantic
from pyasn1.codec.ber import decoder
from pyasn1.type import univ
from pyasn1_modules import rfc2315


class ContentInfo(pydantic.BaseModel):
    content_type: str = pydantic.Field(..., alias='contentType')
    content: bytes

    @pydantic.validator('content_type', pre=True)
    def decode_content_type(cls, value: rfc2315.ContentType | str) -> str:
        if isinstance(value, rfc2315.ContentType):
            value = str(value)
        return value

    @pydantic.validator('content', pre=True)
    def decode_content(cls, value: bytes | univ.Any | univ.OctetString) -> bytes:
        if isinstance(value, univ.Any):
            value, _ = decoder.decode(bytes(value))
            if _:
                raise ValueError("Invalid BER encoding.")
            if not isinstance(value, univ.OctetString):
                raise TypeError(f'Invalid ASN.1 object: {type(value).__name__}')
        if isinstance(value, univ.OctetString):
            value = bytes(value)
        return bytes(value)