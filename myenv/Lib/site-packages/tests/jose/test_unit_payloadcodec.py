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
from typing import Any

import pytest

from ckms import jose
from ckms.core.models import JSONWebSignature
from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload


@pytest.mark.asyncio
async def test_encrypt_fixed_algorithm(codec: jose.PayloadCodec):
    alg = codec.get_key_algorithm('RSA-OAEP')
    assert alg is not None
    payload = codec.encode({'foo': 'bar'}, encrypters=['RSA-OAEP'])
    token = await payload.serialize()
    header, claims = codec.introspect(token)
    assert header.alg == alg


@pytest.mark.asyncio
async def test_sign_fixed_algorithm(codec: jose.PayloadCodec):
    alg = codec.get_key_algorithm('RS256')
    payload = codec.encode({'foo': 'bar'}, signers=['RS256'])
    token = await payload.serialize()
    header, claims = codec.introspect(token)
    assert header.alg == alg


@pytest.mark.asyncio
async def test_introspect_binary(codec: jose.PayloadCodec):
    payload = codec.encode(b'Hello world!', signers=['HS256'])
    token = str.encode(await payload.serialize())
    _, claims = codec.introspect(token)
    assert claims is None


@pytest.mark.asyncio
async def test_introspect_jws_with_model(codec: jose.PayloadCodec):
    class CustomClaimSet(JSONWebToken):
        foo: str

    claims: CustomClaimSet
    payload = codec.encode(
        JSONWebToken.strict(iss='foo', aud='foo', foo='foo', ttl=30),
        signers=['HS256']
    )
    token = str.encode(await payload.serialize())
    _, claims = codec.introspect(token, model=CustomClaimSet)
    assert isinstance(claims, CustomClaimSet), type(claims)
    assert claims is not None
    assert claims.foo == 'foo'


@pytest.mark.asyncio
async def test_introspect_jws(codec: jose.PayloadCodec):
    payload = codec.encode(
        JSONWebToken.strict(iss='foo', aud='foo', foo='foo', ttl=30),
        signers=['HS256']
    )
    token = str.encode(await payload.serialize())
    _, claims = codec.introspect(token)
    assert claims is not None
    assert claims.iss == 'foo'


@pytest.mark.asyncio
async def test_codec_encode_claimset(codec: jose.PayloadCodec):
    payload = await codec.encode(JSONWebToken.strict(iss='foo', aud='foo', ttl=30), signers=['HS256'])
    jwt = await codec.decode(payload)
    assert jwt.aud == {'foo'}
    assert jwt.iss == 'foo'


@pytest.mark.asyncio
async def test_codec_encode_dict(codec: jose.PayloadCodec):
    payload = await codec.encode({'foo': 1}, signers=['HS256'])
    jwt = await codec.decode(payload)
    assert jwt.extra['foo'] == 1


@pytest.mark.asyncio
async def test_codec_encode_jws_with_overriden_typ(codec: jose.PayloadCodec):
    signed = await codec.encode(JSONWebToken(), signers=['HS256'], content_type="at+jwt")
    jwt = await codec.decode(signed, accept={"at+jwt"})
    assert isinstance(jwt, JSONWebToken)


@pytest.mark.asyncio
async def test_codec_encode_jws_with_overriden_can_deserialize_jwt(codec: jose.PayloadCodec):
    signed = await codec.encode(JSONWebToken(), signers=['HS256'], content_type="at+jwt")
    jwt = await codec.decode(signed, accept={"at+jwt"})
    assert isinstance(jwt, JSONWebToken), repr(jwt)


@pytest.mark.asyncio
async def test_codec_encode_and_sign_jwt(codec):
    jwt = JSONWebToken(foo=1)
    payload = await codec.encode(jwt, signers=['HS256'])
    decoded = await codec.decode(payload)
    assert isinstance(decoded, JSONWebToken), repr(decoded)


@pytest.mark.asyncio
async def test_codec_decode_jws(codec, encoded_jwt, jwt):
    payload = await codec.decode(encoded_jwt)
    assert isinstance(payload, JSONWebToken)


@pytest.mark.asyncio
async def test_codec_decode_jws_jwt(codec, encoded_jwt, jwt):
    payload = await codec.decode(encoded_jwt)
    assert jwt.extra.get('foo') == payload.extra.get('foo')


@pytest.mark.asyncio
async def test_codec_decode_jws_payload(codec, encoded_payload, payload):
    decoded = await codec.decode(encoded_payload)
    assert decoded == payload


@pytest.mark.asyncio
async def test_codec_decode_jwe_jwt(codec, encrypted_jwt, jwt):
    decrypted = await codec.decode(encrypted_jwt)
    assert isinstance(jwt, JSONWebToken)
    assert jwt.extra.get('foo') == decrypted.extra.get("foo")


@pytest.mark.asyncio
async def test_codec_decode_jwe_payload(codec, encrypted_payload, payload):
    decrypted = await codec.decode(encrypted_payload)
    assert decrypted == payload


@pytest.mark.asyncio
async def test_deserialize_nested_jws(codec: PayloadCodec):
    jwe = await codec.encode(
        JSONWebToken(foo=1),
        signers=['HS256'],
        encrypters=['RSA-OAEP']
    )
    jwt = await codec.decode(jwe)
    assert isinstance(jwt, JSONWebToken)


@pytest.mark.asyncio
async def test_deserialize_jws_payload(keychain, codec):
    jws = await codec.encode(b"Hello world!", signers=['HS256'])
    assert await codec.decode(jws) == b"Hello world!"


@pytest.mark.asyncio
async def test_deserialize_jwe_payload(keychain, codec):
    jwe = await codec.encode(b"Hello world!", encrypters=['RSA-OAEP'])
    assert await codec.decode(jwe) == b"Hello world!"



@pytest.mark.parametrize("payload", [
    b'Hello world!',
    {'foo': 'bar'}
])
@pytest.mark.parametrize("encrypters", [
    None,
    ['RSA-OAEP'],
    ['RSA-OAEP', 'RSA-OAEP-256'],
])
@pytest.mark.parametrize("signers", [
    ['HS256'],
    ['HS256', 'HS384'],
])
@pytest.mark.asyncio
async def test_deserialize_to_jws(
    payload: bytes | dict[str, Any],
    codec: PayloadCodec,
    signers: list[str],
    encrypters: list[str] | None
):
    token = await codec.encode(
        payload=payload,
        signers=signers,
        encrypters=encrypters
    )
    jws = await codec.jws(token)
    assert isinstance(jws, JSONWebSignature)


@pytest.mark.parametrize("payload", [
    b'Hello world!',
    {'foo': 'bar'}
])
@pytest.mark.parametrize("encrypters", [
    None,
    ['RSA-OAEP'],
    ['RSA-OAEP', 'RSA-OAEP-256'],
])
@pytest.mark.parametrize("signers", [
    ['HS256'],
    ['HS256', 'HS384'],
])
@pytest.mark.asyncio
async def test_deserialize_to_jwt(
    payload: bytes | dict[str, Any],
    codec: PayloadCodec,
    signers: list[str],
    encrypters: list[str] | None
):
    token = await codec.encode(
        payload=payload,
        signers=signers,
        encrypters=encrypters
    )
    if isinstance(payload, bytes):
        with pytest.raises(MalformedPayload):
            await codec.jwt(token)
    else:
        jws, claims = await codec.jwt(token)
        assert isinstance(jws, JSONWebSignature)
        assert isinstance(claims, JSONWebToken)