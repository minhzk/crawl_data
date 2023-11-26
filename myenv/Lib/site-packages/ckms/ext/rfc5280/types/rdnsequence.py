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
# type: ignore
from typing import Optional

from pyasn1.type.base import Asn1Type
from pyasn1.type import univ
from pyasn1_modules import rfc5280

from .relativedistinguishedname import RelativeDistinguishedName


class RDNSequence(list[RelativeDistinguishedName]):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: list[RelativeDistinguishedName] | univ.SetOf | None
    ) -> Optional['RDNSequence']:
        if isinstance(value, rfc5280.Name):
            value = [
                RelativeDistinguishedName.validate(x)
                for x in value['rdnSequence']
            ]
        elif isinstance(value, Asn1Type):
            raise NotImplementedError(type(value))
        return cls(value) if value is not None else None

    def asn1(self) -> rfc5280.Name:
        obj = rfc5280.Name()
        seq = rfc5280.RDNSequence()
        for rdn in self:
            seq.append(rdn.asn1())
        obj['rdnSequence'] = seq
        return obj