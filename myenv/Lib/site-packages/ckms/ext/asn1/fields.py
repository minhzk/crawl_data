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

from pyasn1.type import univ


class ObjectIdentifier(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: str | univ.ObjectIdentifier | None
    ) -> Optional['ObjectIdentifier']:
        if isinstance(value, univ.ObjectIdentifier):
            value = str(value) if value.isValue else None
        return cls(value) if value is not None else None

    def asn1(self) -> univ.ObjectIdentifier:
        return univ.ObjectIdentifier(self)


class Integer(int):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: int | univ.Integer
    ) -> 'Integer':
        if isinstance(value, univ.Integer):
            value = int(value)
        return cls(value)

    def asn1(self) -> univ.Integer:
        return univ.Integer(self)


class BitString(bytes):
    null: bool

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: bytes | univ.BitString | None
    ) -> Optional['BitString']:
        if isinstance(value, univ.BitString):
            value = bytes(value.asOctets()) if value.isValue else None # type: ignore
        return cls(value, null=value is None)

    def __new__(cls, value: bytes | None, null: bool = False):
        self = super().__new__(cls, value or b'')
        self.null = null
        return self

    def asn1(self) -> univ.BitString:
        return univ.BitString.fromOctetString(self) # type: ignore

    def __repr__(self) -> str:
        return bytes.__repr__(self)