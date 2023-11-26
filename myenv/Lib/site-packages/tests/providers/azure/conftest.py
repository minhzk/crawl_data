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

import ckms.core
from ckms.core.models import KeySpecification


ENCRYPTION_KEYS: list[KeySpecification] = []

SIGNING_KEYS_ASYMMETRIC: list[KeySpecification] = [
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'vault': 'unimatrixdev',
        'name': 'ec-sign-p256-sha256'
    }),
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'vault_url': 'https://unimatrixdev.vault.azure.net/',
        'name': 'ec-sign-p384-sha384'
    }),
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'vault_url': 'https://unimatrixdev.vault.azure.net/',
        'name': 'ec-sign-p521-sha512'
    }),
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'algorithm': 'RS256',
        'vault': 'unimatrixdev',
        'name': 'rsa-sign-pkcs1-2048-sha256'
    }),
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'algorithm': 'RS384',
        'vault': 'unimatrixdev',
        'name': 'rsa-sign-pkcs1-2048-sha384'
    }),
    ckms.core.parse_spec({
        'provider': 'azure',
        'use': 'sig',
        'algorithm': 'RS512',
        'vault': 'unimatrixdev',
        'name': 'rsa-sign-pkcs1-2048-sha512'
    }),
]

SIGNING_KEYS_SYMMETRIC: list[KeySpecification] = []

SIGNING_KEYS: list[KeySpecification] = [
    *SIGNING_KEYS_ASYMMETRIC
]

SUPPORTED_KEYS: list[KeySpecification] = [
    *SIGNING_KEYS
]

@pytest.fixture(scope='session')
def supported_keys() -> list[KeySpecification]:
    return SUPPORTED_KEYS