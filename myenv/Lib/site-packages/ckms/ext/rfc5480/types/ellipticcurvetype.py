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
from cryptography.hazmat.primitives.asymmetric import ec

from ckms.ext.asn1 import ObjectIdentifierEnum


class EllipticCurveType(str, ObjectIdentifierEnum):
    SECP256R1 = '1.2.840.10045.3.1.7'
    SECP256K1 = '1.3.132.0.10'
    SECP384R1 = '1.3.132.0.34'
    SECP521R1 = '1.3.132.0.35'

    @classmethod
    def fromcurve(cls, curve: ec.EllipticCurve) -> 'EllipticCurveType':
        return getattr(cls, str.upper(curve.name))

    def get(self) -> ec.EllipticCurve:
        return getattr(ec, self.name)()