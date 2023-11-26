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
from typing import Any

import pydantic
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from pyasn1.type import univ
from pyasn1_modules import rfc5280

from ckms.ext import asn1
from ckms.ext.rfc5480.types import ECParameters
from ckms.ext.asn1.fields import ObjectIdentifier
from ckms.utils import normalize_ec_signature
from ckms.utils import bytes_to_number


class AlgorithmIdentifier(asn1.ASN1Model):
    __asn1spec__: type[rfc5280.AlgorithmIdentifier] = rfc5280.AlgorithmIdentifier
    name: ObjectIdentifier = pydantic.Field(..., alias='algorithm')
    parameters: univ.Any | ECParameters | None

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        params = values.get('parameters')
        if params is None:
            return values
        if not isinstance(params, ECParameters) and params.isValue:
            params = asn1.decode_der(value=params)
            if params:
                # TODO: This assumes that there are params only with EC
                values['parameters'] = ECParameters.parse_obj({
                    'namedCurve': str(params)
                })
        return values

    @pydantic.validator('name', pre=True)
    def validate_name(cls, value: str | univ.ObjectIdentifier) -> str:
        return str(value)

    def encode_signature(self, signature: bytes) -> bytes:
        if isinstance(self.parameters, ECParameters):
            assert len(signature) in {64, 96, 132}, len(signature)
            l = int(len(signature) / 2)
            signature = encode_dss_signature(
                r=bytes_to_number(signature[:l]),
                s=bytes_to_number(signature[l:])
            )
        return signature

    def normalize_signature(self, signature: bytes) -> bytes:
        if isinstance(self.parameters, ECParameters):
            curve = self.parameters.curve.get()
            signature = normalize_ec_signature(
                l=(curve.key_size + 7) // 8,
                sig=signature
            )
        return signature