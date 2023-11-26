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
"""Declares :class:`GenerateKeySpec`."""
from typing import Any
from typing import Literal
from typing import TypeAlias
from typing_extensions import Annotated

import pydantic

from .edwardscurvetype import EdwardsCurveType
from .ellipticcurvetype import EllipticCurveType


__all__: list[str] = [
    'GenerateAES',
    'GenerateEllipticCurve',
    'GenerateHMAC',
    'GenerateKeySpec',
    'GenerateOKP',
    'GenerateRSA',
    'KeyType'
]


class GenerateRSA(pydantic.BaseModel):
    kty: Literal['RSA'] = 'RSA'
    length: int


class GenerateOKP(pydantic.BaseModel):
    kty: Literal['OKP'] = 'OKP'
    curve: EdwardsCurveType


class GenerateEllipticCurve(pydantic.BaseModel):
    kty: Literal['EC'] = 'EC'
    curve: EllipticCurveType


class GenerateAES(pydantic.BaseModel):
    kty: Literal['oct'] = 'oct'
    length: int
    use: Literal['enc']


class GenerateHMAC(pydantic.BaseModel):
    kty: Literal['oct'] = 'oct'
    length: int
    use: Literal['sig']


GenerateSymmetric = Annotated[
    GenerateHMAC|GenerateAES,
    pydantic.Field(discriminator='use')
]

KeyType: TypeAlias = (
    GenerateRSA |
    GenerateOKP |
    GenerateEllipticCurve |
    GenerateSymmetric
)


class GenerateKeySpec(pydantic.BaseModel):
    __root__: Annotated[
        KeyType,
        pydantic.Field(discriminator='kty')
    ]

    @classmethod
    def parse_spec(
        cls,
        spec: dict[str, Any]
    ) -> KeyType:
        """Parse the spec as the appropriate key type."""
        return cls.parse_obj(spec).__root__