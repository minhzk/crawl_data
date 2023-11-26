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
import ipaddress
from typing import Literal

from pyasn1.type import univ

from .name import Name


class IPAddressName(Name):
    kind: Literal['iPAddress'] = 'iPAddress'
    value: ipaddress.IPv4Address | ipaddress.IPv6Address

    @classmethod
    def parse_value(
        cls,
        value: bytes | str | univ.OctetString
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        if isinstance(value, univ.OctetString):
            value = bytes(value)
        return ipaddress.ip_address(value)

    def encode_value(self) -> bytes:
        return self.value.packed
