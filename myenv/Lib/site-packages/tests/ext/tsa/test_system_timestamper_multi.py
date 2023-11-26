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

from ckms.ext.tsa import Timestamper


@pytest.fixture
def timestamper() -> Timestamper:
    return Timestamper.fromlist([
        {'url': "http://tss.accv.es:8318/tsa"},
        {'url': "http://timestamp.apple.com/ts01"},
        {'url': "http://timestamp.digicert.com"},
        {'url': "http://aatl-timestamp.globalsign.com/tsa/aohfewat2389535fnasgnlg5m23"},
        {'url': "http://tsa.izenpe.com"},
        {'url': "http://kstamp.keynectis.com/KSign/"},
        {'url': "http://tsa.quovadisglobal.com/TSS/HttpTspServer"},
    ])


@pytest.mark.asyncio
async def test_timestamp_with_default_signatures(
    data: bytes,
    client: AsyncClient,
    timestamper: Timestamper
):
    responses = await timestamper.timestamp(client, data)
    assert len(responses) == 1


@pytest.mark.asyncio
async def test_timestamp_with_min_signatures(
    data: bytes,
    client: AsyncClient,
    timestamper: Timestamper
):
    responses = await timestamper.timestamp(client, data, min_signatures=3)
    assert len(responses) == 3