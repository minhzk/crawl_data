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
"""Declares :class:`KeySpecification`."""
from typing import Any

import pydantic
from typing_extensions import Annotated

from ckms.core import models
from ckms.types import Algorithm
from .types import EdwardsCurveKeySpecification
from .types import EllipticCurveKeySpecification
from .types import RSAKeySpecification
from .types import SymmetricKeySpecification


class KeySpecification(models.BaseKeySpecification):
    __root__: Annotated[
        EllipticCurveKeySpecification |
        RSAKeySpecification |
        EdwardsCurveKeySpecification |
        SymmetricKeySpecification,
        pydantic.Field(discriminator='kty')
    ]

    @classmethod
    def generate(cls, **kwargs: Any) -> models.KeySpecification:
        return cls.parse_obj(kwargs)

    @classmethod
    def parse_obj(cls: type[pydantic.BaseModel], obj: Any) -> models.KeySpecification:
        return super().parse_obj(obj).__root__ # type: ignore

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        spec: dict[str, Any] = values.get('__root__', {})
        alg: str | None | Algorithm = spec.get('alg') or spec.get('algorithm')
        if alg is not None:
            alg = Algorithm.get(alg)
            spec.update({
                'kty': alg.kty
            })

        return values