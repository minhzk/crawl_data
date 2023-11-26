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
import asyncio

import pytest
import pytest_asyncio

from ckms.core import Keychain
from ckms.core.models import KeySpecification


@pytest.fixture(scope='session')
def decrypter() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def encrypter() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def signer() -> Keychain:
    return Keychain()


@pytest.fixture(scope='session')
def verifier() -> Keychain:
    return Keychain()


@pytest_asyncio.fixture(scope='session', autouse=True) # type: ignore
async def setup_keys(
    decrypter: Keychain,
    encrypter: Keychain,
    signer: Keychain,
    verifier: Keychain,
    supported_keys: list[KeySpecification]
):
    await asyncio.gather(*supported_keys)
    for spec in supported_keys:
        assert spec.kid is not None
        assert spec.is_loaded()
        public = spec.as_public() if spec.is_asymmetric() else spec
        if spec.can_sign():
            signer.add(spec.kid, spec)
            verifier.add(public.kid, public) # type: ignore
        if spec.can_decrypt():
            decrypter.add(spec.kid, spec)
            encrypter.add(public.kid, public) # type: ignore