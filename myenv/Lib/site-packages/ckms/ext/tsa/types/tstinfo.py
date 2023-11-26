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
import datetime

import pydantic

from pyasn1.type.useful import GeneralizedTime
from pyasn1.type import univ
from pyasn1_modules import rfc2315
from pyasn1_modules import rfc3161

from ckms.ext import asn1
from ckms.ext.rfc3161.oid import TSTInfoOID
from .messageimprint import MessageImprint


class TSTInfo(pydantic.BaseModel):
    version: int
    policy: str | None
    serial_number: int = pydantic.Field(..., alias='serialNumber')
    generated: datetime.datetime = pydantic.Field(..., alias='genTime')
    ordering: bool | None
    nonce: int | None
    message_imprint: MessageImprint = pydantic.Field(..., alias='messageImprint')
    #tsa: str | None

    @classmethod
    def from_signed_data(cls, content_info: rfc2315.ContentInfo) -> 'TSTInfo':
        oid = str(content_info['contentType']) # type: ignore
        if str(oid) != TSTInfoOID:
            raise ValueError(f'Unexpected content type: {oid}')
        return cls.parse_obj(
            asn1.decode_ber(
                value=content_info['content'], # type: ignore
                spec=rfc3161.TSTInfo()
            )
        )

    @pydantic.validator('generated', pre=True)
    def validate_generated(cls, value: datetime.datetime | GeneralizedTime) -> datetime.datetime | str:
        if isinstance(value, GeneralizedTime):
            value = datetime.datetime.strptime(str(value), '%Y%m%d%H%M%SZ')
        return value

    @pydantic.validator('nonce', pre=True)
    def validate_nonce(cls, value: int | univ.Integer | None) -> int | None:
        if isinstance(value, univ.Integer):
            value = int(value) if value.isValue else None
        return value

    @pydantic.validator('policy', pre=True)
    def validate_policy(cls, value: str | rfc3161.TSAPolicyId | None) -> str | None:
        if isinstance(value, rfc3161.TSAPolicyId):
            value = str(value) if value.isValue else None
        return value

    @pydantic.validator('serial_number', pre=True)
    def validate_serial_number(cls, value: int | univ.Integer) -> int:
        if isinstance(value, univ.Integer):
            value = int(value)
        return value

    #@pydantic.validator('tsa', pre=True)
    #def validate_tsa(cls, value: str | rfc3161.GeneralName) -> str:
    #    if isinstance(value, rfc3161.GeneralName):
    #        value = str(value)
    #    return value