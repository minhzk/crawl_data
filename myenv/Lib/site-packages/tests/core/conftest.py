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
# type: ignore
import copy
import os
from typing import Any

import pytest
import pytest_asyncio
from jwcrypto.common import json_encode # type: ignore
from jwcrypto.jwe import JWE
from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS

from ckms.core import Keychain
from ckms.utils import b64encode


DATA: bytes = os.urandom(16)


@pytest.fixture
def data() -> bytes:
    return DATA


@pytest.fixture
def jwe():
    payload = b'Hello world!'
    k1 = JWK.generate(kty='oct', size=256)
    k2 = JWK.generate(kty='oct', size=256)
    jwe = JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512"
        })
    )
    jwe.add_recipient(k1, {'foo': 1})
    jwe.add_recipient(k2)
    return jwe


@pytest.fixture
def jwe_single():
    payload = b'Hello world!'
    k1 = JWK.generate(kty='oct', size=256)
    jwe = JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512",
            'foo': 1
        })
    )
    jwe.add_recipient(k1, {'bar': 1})
    return jwe


@pytest.fixture
def jws() -> JWS:
    payload = 'Hello world!'
    k1 = JWK.generate(kty='oct', size=32) # type: ignore
    k2 = JWK.generate(kty='oct', size=32) # type: ignore
    k3 = JWK.generate(kty='oct', size=32) # type: ignore
    k4 = JWK.generate(kty='oct', size=32) # type: ignore
    jws = JWS(payload)
    jws.add_signature(k1, 'HS256', protected={'foo': 1}, header={'bar': 1})
    jws.add_signature(k2, 'HS256', protected={'foo': 2})
    return jws


@pytest.fixture
def jws_single() -> JWS:
    payload = 'Hello world!'
    k1 = JWK.generate(kty='oct', size=32) # type: ignore
    jws = JWS(payload)
    jws.add_signature(k1, 'HS256', protected={'foo': 1, 'alg': 'HS256'}, header={'bar': 1})
    return jws


@pytest.fixture
def multi_jwe(jwe: JWE) -> bytes:
    return b64encode(jwe.serialize(compact=False))


@pytest.fixture
def multi_jws(jws: JWS) -> bytes:
    return b64encode(jws.serialize(compact=False))


@pytest.fixture
def flattened_jwe(jwe_single: JWE) -> bytes:
    return b64encode(jwe_single.serialize(compact=False))


@pytest.fixture
def flattened_jws(jws_single: JWS) -> bytes:
    return b64encode(jws_single.serialize(compact=False))


@pytest.fixture
def compact_jwe(jwe_single: JWE) -> str:
    return jwe_single.serialize(compact=True)


@pytest.fixture
def compact_jws(jws_single: JWS) -> str:
    return jws_single.serialize(compact=True)


@pytest_asyncio.fixture(scope='session')
async def keychain(keys: dict[str, Any]):
    keychain = Keychain()
    keychain.configure(keys=copy.deepcopy(keys))
    await keychain
    return keychain

@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_keychain(keychain: Keychain):
    await keychain