# pylint: skip-file
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
from typing import cast
from typing import Any

import pydantic
from cryptography.hazmat.primitives.asymmetric.types import PUBLIC_KEY_TYPES

from ckms.types import Algorithm
from ckms.types import JSONWebKey
from ckms.types import KeyOperationType
from ckms.types import KeyUseType
from ckms.core.models import KeySpecification
from ckms.utils import b64encode
from .types import AzureConsumer


class AzureKeySpecification(KeySpecification, AzureConsumer):
    algorithm: Algorithm = Algorithm.get('null')
    kty: str | None # type: ignore
    use: KeyUseType
    name: str
    vault: str | None
    vault_url: str
    jwk: JSONWebKey | None
    hsm: bool = False

    #: The key version. If :attr:`version` is ``None``, then the latest
    #: version is used.
    version: str | None

    @property
    def azure_key_id(self) -> str:
        return f'{self.vault_url}/keys/{self.name}/{self.version}'

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        vault = values.get('vault')
        if vault and not values.get('vault_url'):
            values['vault_url'] = f"https://{vault}.vault.azure.net/"
        return values

    @pydantic.validator('vault_url', pre=False)
    def postprocess_vault_url(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            value = str.rstrip(value, '/')
        return value

    def get_public_key(self) -> PUBLIC_KEY_TYPES | None:
        assert self.jwk is not None
        return self.jwk.get_public_key()

    async def load(self) -> KeySpecification:
        async with self.key_client(self.vault_url) as client:
            obj = await client.get_key(self.name, version=self.version)
            self.kty = str(obj.key_type)
            if self.kty in {'EC-HSM', 'RSA-HSM'}: # pragma: no cover
                self.kty, _ = str.split(self.kty, '-') # type: ignore
                self.hsm = True
            jwk = cast(JSONWebKey, obj.key)
            self.kid = self.provider.calculate_kid(obj.id)
            self.key_ops = {KeyOperationType(x) for x in obj.key_operations}
            if jwk.crv: # type: ignore
                self.algorithm = Algorithm.get_for_curve(jwk.crv)
                self.curve = jwk.crv
            else:
                assert self.use is not None
                if self.algorithm is None: # pragma: no cover
                    self.algorithm = Algorithm.default(self.kty, self.use.value)
            self.jwk = JSONWebKey.parse_obj({
                **{
                    k: bytes.decode(b64encode(v)) if isinstance(v, bytes) else v
                    for  k, v in jwk.__dict__.items()
                },
                'alg': self.algorithm,
                'use': self.use,
                'kid': self.kid,
                'kty': self.kty
            })
            if self.version is None:
                self.version = obj.properties.version

        assert self.algorithm
        assert self.kty
        assert self.use
        assert self.key_ops
        self.loaded = True
        return self

    def __hash__(self) -> int: # type: ignore
        return str.__hash__(f'{self.vault_url}/{self.name}')
