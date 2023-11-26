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

from headless.core.httpx import Client
from headless.types import IClient

from ..server import Server


__all__: list[str] = [
    'client',
    'test_discover'
]


@pytest_asyncio.fixture # type: ignore
async def client(server_url: str) -> AsyncGenerator[IClient[Any, Any], None]:
    client = Client(base_url=server_url)
    await client.__aenter__()
    yield client
    await client.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_discover(client: IClient[Any, Any]):
    server = Server(client)
    await server