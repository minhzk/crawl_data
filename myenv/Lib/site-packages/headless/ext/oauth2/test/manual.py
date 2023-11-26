# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from headless.ext.oauth2 import Client
from headless.types import IClient


__all__: list[str] = [
    'client',
    'test_authorize'
]


@pytest_asyncio.fixture # type: ignore
async def client(
    server_params: dict[str, Any
]) -> AsyncGenerator[IClient[Any, Any], None]:
    client = Client(**server_params)
    await client.__aenter__()
    yield client
    await client.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_authorize(
    client: Client,
):
    url = await client.authorize(
        state='test',
        redirect_uri='https://python-headless.localhost.unimatrixone.io/oauth2/callback'
    )
    raise Exception(url)