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
import copy
from typing import Any

import pytest
import pytest_asyncio

import ckms.core
from ckms.core import Keychain
from ckms.jose import PayloadCodec
from ckms.jose.decoder import Decoder
from ckms.jose.encoder import Encoder
from ckms.types import JSONWebToken
from ckms.types import IKeychain


@pytest.fixture
def decoder(keychain: Keychain) -> Decoder:
    return Decoder(decrypter=keychain, verifier=keychain)


@pytest.fixture
def encoder(keychain: Keychain) -> Encoder:
    return Encoder(encrypter=keychain, signer=keychain)


@pytest.fixture
def codec(keychain: IKeychain):
    assert keychain is not None
    return PayloadCodec(
        signer=keychain,
        verifier=keychain,
        encrypter=keychain,
        decrypter=keychain
    )


@pytest.fixture
def payload() -> bytes:
    return b'Hello world!'


@pytest.fixture
def jwt() -> JSONWebToken:
    return JSONWebToken.parse_obj({'foo': 1})


@pytest_asyncio.fixture # type: ignore
async def encoded_jwt(codec: PayloadCodec, jwt: JSONWebToken) -> bytes:
    return str.encode(await codec.encode(jwt, signers=['HS256']))


@pytest_asyncio.fixture # type: ignore
async def encoded_payload(codec: PayloadCodec, payload: bytes) -> bytes:
    return str.encode(await codec.encode(payload, signers=['HS256']))


@pytest_asyncio.fixture # type: ignore
async def encrypted_jwt(codec: PayloadCodec, jwt: JSONWebToken) -> bytes:
    return str.encode(await codec.encode(jwt, encrypters=['RSA-OAEP']))


@pytest_asyncio.fixture # type: ignore
async def encrypted_payload(codec: PayloadCodec, payload: bytes) -> bytes:
    return str.encode(await codec.encode(payload, encrypters=['RSA-OAEP']))