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
import contextlib
from typing import cast
from typing import AsyncIterator

from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.keys.crypto.aio import CryptographyClient


class AzureConsumer:
    __module__: str = 'ckms.ext.azure.types'

    def credential(self) -> DefaultAzureCredential:
        return DefaultAzureCredential()

    @contextlib.asynccontextmanager
    async def crypto_client(self, key_id: str) -> AsyncIterator[CryptographyClient]:
        async with self.credential() as credential:
            async with CryptographyClient(key_id, credential=credential) as client: # type: ignore
                yield cast(CryptographyClient, client)

    @contextlib.asynccontextmanager
    async def key_client(self, vault_url: str) -> AsyncIterator[KeyClient]:
        async with self.credential() as credential:
            async with KeyClient(vault_url=vault_url, credential=credential) as client: # type: ignore
                yield cast(KeyClient, client)