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
from typing import Any
from typing import Sized

import pytest

from ckms.core import Keychain
from ckms.core import const
from ckms.types import JSONWebKeySet


@pytest.fixture
def tagged_keys() -> dict[str, Any]:
    return {
        'HS256': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS256',
            'key': {'length': 32},
            'tags': {'foo'}
        },
        'HS384': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS384',
            'key': {'length': 32},
            'tags': {'bar'}
        },
        'HS512': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS512',
            'key': {'length': 32},
            'tags': {'foo', 'bar'}
        },
    }


@pytest.mark.asyncio
async def test_fromdict(keys: dict[str, Any]):
    kc = Keychain.fromdict(keys)
    await kc
    assert len(kc) == len(keys) * 2


def test_keychain_length(
    keychain: Keychain,
    keys: Sized
):
    assert len(keychain) == len(keys) * 2


@pytest.mark.parametrize("algorithm", const.ALGORITHMS)
def test_keychain_has(algorithm: str, keychain: Keychain):
    assert keychain.has(algorithm), algorithm


@pytest.mark.parametrize("algorithm", const.ALGORITHMS)
def test_add_duplicate_raises_valueerror(algorithm: str, keychain: Keychain):
    with pytest.raises(ValueError):
        keychain.add(algorithm, {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS256',
            'use': 'sig',
            'key': {'length': 32}
        })



@pytest.mark.parametrize("params", [
    {'kid': 'abc'},
    {'algorithm': 'foo'},
    {'use': 'bar'},
])
def test_filter_with_unloaded_raises_runtimeerror(params: dict[str, Any]):
    keychain = Keychain()
    with pytest.raises(RuntimeError):
        keychain.add('abc', {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS256',
            'use': 'sig',
            'key': {'length': 32}
        })
        keychain.filter(**params)


def test_filter_with_non_existing_kid_returns_empty(keychain: Keychain):
    result = keychain.filter(kid='abc')
    assert len(result) == 0


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS)
@pytest.mark.asyncio
async def test_asymmetric_key_is_not_aliased(
    algorithm: str,
    keychain: Keychain
):
    spec = keychain.get(algorithm)
    public = keychain.get(spec.kid) # type: ignore
    assert spec != public
    assert spec.kid == public.kid


@pytest.mark.parametrize("algorithm", const.SYMMETRIC_ALGORITHMS)
@pytest.mark.asyncio
async def test_symmetric_key_is_aliased(
    algorithm: str,
    keychain: Keychain
):
    spec = keychain.get(algorithm)
    aliased = keychain.get(spec.kid) # type: ignore
    assert spec == aliased
    assert spec.kid == aliased.kid


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_asymmetric(
    algorithm: str,
    keychain: Keychain
):
    result = keychain.filter(algorithm=algorithm)
    assert len(result) == 2


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS&const.SIGNING_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_use_asymmetric_sig(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, use='sig')) == 2
    assert len(keychain.filter(algorithm=algorithm, use='enc')) == 0


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS-const.SIGNING_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_use_asymmetric_enc(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, use='sig')) == 0
    assert len(keychain.filter(algorithm=algorithm, use='enc')) == 2


@pytest.mark.parametrize("algorithm", const.SYMMETRIC_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_symmetric(
    algorithm: str,
    keychain: Keychain
):
    result = keychain.filter(algorithm=algorithm)
    assert len(result) == 2


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS&const.DH_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_op_asymmetric_dh(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, op='decrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveKey')) == 2
    assert len(keychain.filter(algorithm=algorithm, op='deriveBits')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='encrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='sign')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='verify')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='unwrapKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='wrapKey')) == 0


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS&const.ENCRYPTION_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_op_asymmetric_enc(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, op='decrypt')) == 1
    assert len(keychain.filter(algorithm=algorithm, op='deriveKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveBits')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='encrypt')) == 2
    assert len(keychain.filter(algorithm=algorithm, op='sign')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='verify')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='unwrapKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='wrapKey')) == 0


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS&const.SIGNING_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_op_asymmetric_sig(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, op='decrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveBits')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='encrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='sign')) == 1
    assert len(keychain.filter(algorithm=algorithm, op='verify')) == 2
    assert len(keychain.filter(algorithm=algorithm, op='unwrapKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='wrapKey')) == 0


@pytest.mark.parametrize("algorithm", const.ASYMMETRIC_ALGORITHMS&const.KEYWRAP_ALGORITHMS)
@pytest.mark.asyncio
async def test_filter_by_algorithm_and_op_asymmetric_wrap(
    algorithm: str,
    keychain: Keychain
):
    assert len(keychain.filter(algorithm=algorithm, op='decrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveKey')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='deriveBits')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='encrypt')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='sign')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='verify')) == 0
    assert len(keychain.filter(algorithm=algorithm, op='unwrapKey')) == 1
    assert len(keychain.filter(algorithm=algorithm, op='wrapKey')) == 2


@pytest.mark.parametrize("tags", [
    "foo",
    {"foo"},
    ["foo"]
])
@pytest.mark.asyncio
async def test_tagged(
    tags: list[str] | str | set[str],
    tagged_keys: dict[str, Any]
):
    kc = Keychain()
    kc.configure(tagged_keys)
    await kc
    assert len(kc) == len(tagged_keys) * 2
    tagged = kc.tagged(tags)
    assert len(tagged) == 4


@pytest.mark.asyncio
async def test_tagged_must_be_loaded(tagged_keys: dict[str, Any]):
    kc = Keychain()
    kc.configure(tagged_keys)
    with pytest.raises(RuntimeError):
        kc.tagged('foo')


def test_keychain_to_jwks_public(
    keychain: Keychain,
    asymmetric_keys: Sized
):
    jwks = keychain.as_jwks(private=False)
    assert isinstance(jwks, JSONWebKeySet)
    assert len(jwks) == len(asymmetric_keys)


def test_keychain_to_jwks_private(
    keychain: Keychain,
    asymmetric_keys: Sized
):
    with pytest.raises(NotImplementedError):
        keychain.as_jwks(private=True)