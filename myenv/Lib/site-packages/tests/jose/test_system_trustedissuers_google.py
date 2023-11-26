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

import google.auth
import google.auth.transport.requests
import google.auth.exceptions
import pytest

from ckms.jose import TrustedIssuers
import pytest_asyncio


@pytest.fixture(scope='session')
def id_token() -> str:
    try:
        creds, _ = cast(tuple[Any, Any], google.auth.default()) # type: ignore
        creds.refresh(google.auth.transport.requests.Request())
    except google.auth.exceptions.RefreshError:
        pytest.skip()
    return creds.id_token


@pytest_asyncio.fixture(scope='session') # type: ignore
async def trust() -> TrustedIssuers:
    trust = TrustedIssuers()
    trust.trust("accounts.google.com")
    await trust
    return trust


@pytest.mark.parametrize("issuer", [
    "accounts.google.com",
    "https://accounts.google.com"
])
@pytest.mark.asyncio
async def test_trust(issuer: str):
    trust = TrustedIssuers()
    trust.trust(issuer=issuer)
    await trust