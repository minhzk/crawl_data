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
import pydantic
from cryptography.hazmat.primitives.asymmetric import ec
from pyasn1_modules import rfc5480

from ckms.ext import asn1
from .ellipticcurvetype import EllipticCurveType


class ECParameters(asn1.ASN1Model):
    __asn1spec__: type[rfc5480.ECParameters] = rfc5480.ECParameters
    curve: EllipticCurveType = pydantic.Field(..., alias='namedCurve')

    @pydantic.validator('curve', pre=True)
    def validate_curve(
        cls,
        value: ec.EllipticCurve | str | EllipticCurveType
    ) -> str | EllipticCurveType:
        if isinstance(value, ec.EllipticCurve):
            value = EllipticCurveType.fromcurve(value)
        return value