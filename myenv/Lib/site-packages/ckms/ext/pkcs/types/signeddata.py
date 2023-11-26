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
# type: ignore
from typing import Any

import pydantic
from pyasn1.type import univ
from pyasn1_modules import rfc2315

from ckms.ext.x509.types import AlgorithmIdentifier
from ckms.ext.x509.types import Certificate
from .contentinfo import ContentInfo
from .signerinfo import SignerInfo


class SignedData(pydantic.BaseModel):
    version: int
    digest_algorithms: set[AlgorithmIdentifier]
    content_info: ContentInfo
    certificates: set[Certificate] | None = None
    signers: list[SignerInfo] = pydantic.Field(..., alias='signerInfos')

    @property
    def content(self) -> bytes:
        return self.content_info.content

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        if isinstance(values.get('version'), rfc2315.Version):
            values['version'] = int(values['version'])
        algorithms = values['digest_algorithms'] = list(values.get('digestAlgorithms') or [])
        for i, algorithm in enumerate(algorithms):
            algorithms[i] = AlgorithmIdentifier(str(algorithm['algorithm']))
        values['content_info'] = values.get('contentInfo')
        return values

    @pydantic.validator('certificates', pre=True)
    def validate_certificates(
        cls,
        value: set[Certificate] | rfc2315.ExtendedCertificatesAndCertificates | None
    ) -> list[Any] | set[Certificate] | None:
        if isinstance(value, univ.SetOf):
            value = [x for x in value]
        return value

    @pydantic.validator('signers', pre=True)
    def validate_signers(
        cls,
        value: set[SignerInfo] | rfc2315.SignerInfo | None
    ) -> list[Any] | set[SignerInfo] | None:
        if isinstance(value, univ.SetOf):
            value = [x for x in value]
        return value