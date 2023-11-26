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
import pytest_asyncio

from ckms.core import parse_spec
from ckms.core.models import KeySpecification
from ckms.types import JSONWebKey


@pytest_asyncio.fixture(scope='session') # type: ignore
async def key() -> KeySpecification:
    return await parse_spec({
        'provider': 'google',
        'project': 'unimatrixdev',
        'location': 'europe-west4',
        'keyring': 'local',
        'key': 'ec_sign_p256_sha256',
        'version': 5,
        'certificate': {
            'uri': 'https://certs.unimatrixone.io/DevelopmentTestCertificateG5.crt'
        }
    })


@pytest.fixture(scope='session')
def jwk(key: KeySpecification) -> JSONWebKey:
    return JSONWebKey.parse_obj(key.as_public().as_jwk(private=False))


def test_key_has_x5c(jwk: JSONWebKey):
    assert jwk.x5c is not None


def test_key_has_x5t(jwk: JSONWebKey):
    assert jwk.x5t is not None


def test_key_has_x5t_sha256(jwk: JSONWebKey):
    assert jwk.x5t_sha256 is not None


def test_key_has_x5u(jwk: JSONWebKey):
    assert jwk.x5u is not None