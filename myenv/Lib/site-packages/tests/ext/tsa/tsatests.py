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
import pytest
from httpx import AsyncClient

from ckms.ext.tsa import TimestampingAuthority
from ckms.ext.tsa.types import TimeStampResp


__all__: list[str] = [
    'test_create_timestamp_from_bytes'
]


@pytest.mark.asyncio
async def test_create_timestamp_from_bytes(
    client: AsyncClient,
    tsa: TimestampingAuthority,
    data: bytes,
    digest: bytes
):
    response = await tsa.timestamp(
        client=client,
        data=data,
        digest='sha256'
    )
    assert isinstance(response, TimeStampResp)
    info = response.get_tst_info()
    assert info is not None, response
    assert response.token is not None
    response.token.verify(tsa.certificate)