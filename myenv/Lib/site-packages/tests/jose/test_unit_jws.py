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
from typing import Any

import pytest

from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken


@pytest.mark.parametrize("signers", [
    ['HS256'],
    ['HS256', 'HS384'],
])
@pytest.mark.asyncio
async def test_jwt_serialization_is_valid(
    codec: PayloadCodec,
    signers: list[str]
):
    t1 = await codec.encode({'foo': 'bar'}, signers=signers)
    j1 = await codec.jws(t1)
    t2 = j1.json()
    j2 = await codec.jws(t2)
    jwt = await codec.decode(t2, verify=True)
    assert isinstance(jwt, JSONWebToken)
    assert j1.signatures[0] == j2.signatures[0]


@pytest.mark.parametrize("payload", [
    'Hello world!',
    b'Hello world!'
])
@pytest.mark.parametrize("signers", [
    ['HS256'],
    ['HS256', 'HS384'],
])
@pytest.mark.asyncio
async def test_jws_serialization_is_valid(
    codec: PayloadCodec,
    signers: list[str],
    payload: Any
):
    t1 = await codec.encode(payload, signers=signers)
    j1 = await codec.jws(t1)
    t2 = j1.json()
    j2 = await codec.jws(t2)
    jwt = await codec.decode(t2, verify=True)
    assert isinstance(jwt, bytes)
    assert j1.signatures[0] == j2.signatures[0]