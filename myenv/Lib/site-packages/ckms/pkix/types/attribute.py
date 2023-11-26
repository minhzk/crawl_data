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
from pyasn1.type import univ
from pyasn1.type.base import Asn1Type
from pyasn1_modules import rfc2985
from pyasn1_modules import rfc5280

from ckms.ext import asn1


OID_SCHEMA: dict[str, type[Asn1Type]] = {
    '1.2.840.113549.1.9.14': rfc2985.Extensions
}


class Attribute(asn1.ASN1Model):
    """An ``Attribute`` as defined in :rfc:`5280`."""
    __asn1spec__: type[rfc5280.Attribute] = rfc5280.Attribute
    type: asn1.fields.ObjectIdentifier
    values: univ.SetOf

    def decode(self, spec: Asn1Type | None = None) -> list[Asn1Type]:
        if spec is None and self.type in OID_SCHEMA:
            spec = OID_SCHEMA[self.type]()
        return [asn1.decode_der(x, spec) for x in self.values] # type: ignore