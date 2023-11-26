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
from typing import cast

from azure.keyvault.keys.crypto import SignatureAlgorithm

from ckms.types import Operation
from ckms.types import EllipticCurveOperation
from ckms.types import RSAOperation
from .models import AzureKeySpecification
from .types import AzureConsumer
from .types import IAzureProvider


class AzureProvider(IAzureProvider, AzureConsumer):
    __module__: str = 'ckms.ext.azure'
    spec: type[AzureKeySpecification] = AzureKeySpecification

    def get_operation_keyspec(self, op: Operation) -> AzureKeySpecification:
        return cast(AzureKeySpecification, op.get_keyspec())

    async def sign_azure(self, op: Operation) -> bytes:
        spec = self.get_operation_keyspec(op)
        async with self.crypto_client(spec.azure_key_id) as client:
            sig = await client.sign(
                algorithm=SignatureAlgorithm(spec.algorithm),
                digest=await op.get_digest()
            )
        return sig.signature

    async def sign_ec(self, op: EllipticCurveOperation) -> bytes:
        return await self.sign_azure(op)

    async def sign_rsa(self, op: RSAOperation) -> bytes:
        return await self.sign_azure(op)