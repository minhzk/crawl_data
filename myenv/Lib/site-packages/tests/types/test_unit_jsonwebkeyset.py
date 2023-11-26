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
from typing import Sized

import pytest

from ckms.core import Keychain
from ckms.core import const
from ckms.types import JSONWebKeySet


@pytest.fixture
def jwks(keychain: Keychain) -> JSONWebKeySet:
    return keychain.as_jwks(private=False)


def test_jwks_contains_asymmetric_keys(
    jwks: JSONWebKeySet,
    asymmetric_keys: Sized
):
    assert len(jwks) == len(asymmetric_keys)


@pytest.mark.parametrize("name", const.ASYMMETRIC_ALGORITHMS)
def test_jwks_has_key(
    keychain: Keychain,
    jwks: JSONWebKeySet,
    name: str
):
    spec = keychain.get(name)
    public = spec.as_public()
    assert jwks.has(public.kid)
    assert not jwks.has(name)


@pytest.mark.parametrize("name", const.ASYMMETRIC_ALGORITHMS)
def test_jwk_properties_match_key(
    keychain: Keychain,
    jwks: JSONWebKeySet,
    name: str
):
    spec = keychain.get(name)
    public = spec.as_public()
    jwk = jwks.get(public.kid)
    assert jwk.alg == public.algorithm
    assert jwk.crv == public.crv
    assert jwk.use == public.use
    assert set(jwk.key_ops) == public.key_ops