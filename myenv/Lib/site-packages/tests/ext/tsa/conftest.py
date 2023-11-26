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
from typing import AsyncIterable

import pytest
import pytest_asyncio
from httpx import AsyncClient

from ckms.ext.tsa import Timestamper
from ckms.ext.tsa import TimestampingAuthority
from ckms.types import Digest
from ckms.types import Message


@pytest_asyncio.fixture # type: ignore
async def client() -> AsyncIterable[AsyncClient]:
    async with AsyncClient() as client:
        yield client


@pytest.fixture
def data() -> bytes:
    return b'Hello world!'


@pytest_asyncio.fixture # type: ignore
async def digest(message: Message) -> Digest:
    return Digest.frombytes('sha256', bytes(message))


@pytest.fixture
def message(data: bytes) -> Message:
    return Message(buf=data)


@pytest.fixture
def timestamper(tsa: TimestampingAuthority) -> Timestamper:
    return Timestamper([tsa])