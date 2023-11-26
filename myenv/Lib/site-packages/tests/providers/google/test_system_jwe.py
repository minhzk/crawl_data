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
from ckms.core import Keychain
from ckms.core.models import KeySpecification
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload
from .conftest import ENCRYPTION_KEYS



@pytest.mark.parametrize("spec", ENCRYPTION_KEYS)
class TestProviderJWE:

    @pytest.mark.parametrize("pt", [
        b"Hello world!",
        {'foo': 1}
    ])
    @pytest.mark.asyncio
    async def test_encrypt_and_decrypt(
        self,
        encrypter: Keychain,
        decrypter: Keychain,
        spec: KeySpecification,
        pt: str | dict[str, Any]
    ):
        c1 = PayloadCodec(decrypter=decrypter)
        c2 = PayloadCodec()
        jwe = await c1.encode(pt, encrypters=[spec])
        payload = await c1.decode(jwe)
        if isinstance(pt, bytes):
            assert pt == payload
        elif isinstance(pt, dict):
            assert isinstance(payload, JSONWebToken), jwe
        with pytest.raises(MalformedPayload):
            await c2.decode(jwe)