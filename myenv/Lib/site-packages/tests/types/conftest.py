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

import pytest_asyncio

from ckms.core import Keychain


@pytest_asyncio.fixture(scope='session') # type: ignore
async def keychain(keys: dict[str, Any]):
    keychain = Keychain()
    keychain.configure(keys=copy.deepcopy(keys))
    await keychain
    return keychain


@pytest_asyncio.fixture(scope='session', autouse=True) # type: ignore
async def setup_keychain(keychain: Keychain):
    await keychain