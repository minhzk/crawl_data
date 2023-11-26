# pylint: skip-file
# type: ignore
import json

import jwcrypto.jwe
import jwcrypto.jwk
import pydantic
import pytest
from jwcrypto.common import json_encode

from ckms.core.models import JSONWebEncryption
from ckms.core.models import JSONWebEncryptionFlattened
from ckms.core.models import JSONWebEncryptionWithRecipients
from ckms.utils import b64encode


@pytest.fixture
def token():
    payload = b'Hello world!'
    k1 = jwcrypto.jwk.JWK.generate(kty='oct', size=256)
    k2 = jwcrypto.jwk.JWK.generate(kty='oct', size=256)
    jwe = jwcrypto.jwe.JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512"
        })
    )
    jwe.add_recipient(k1, {'foo': 1})
    jwe.add_recipient(k2, {'bar': 2})
    return jwe


@pytest.fixture
def token_single():
    payload = b'Hello world!'
    k1 = jwcrypto.jwk.JWK.generate(kty='oct', size=256)
    jwe = jwcrypto.jwe.JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512",
            'bar': 2
        })
    )
    jwe.add_recipient(k1, {'foo': 1})
    return jwe


def test_parse_jwe_multi_recipient(token: jwcrypto.jwe.JWE):
    obj = JSONWebEncryption.parse_obj(json.loads(token.serialize()))
    assert isinstance(obj.__root__, JSONWebEncryptionWithRecipients)
    assert len(obj.recipients) == 2


def test_parse_jwe_single_recipient():
    payload = b'Hello world!'
    k1 = jwcrypto.jwk.JWK.generate(kty='oct', size=256)
    jwe = jwcrypto.jwe.JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512"
        })
    )
    jwe.add_recipient(k1)
    obj = JSONWebEncryption.parse_obj(json.loads(jwe.serialize()))
    header = obj.header
    assert isinstance(obj.__root__, JSONWebEncryptionFlattened)
    assert len(obj.recipients) == 1


def test_protected_and_unprotected_header_must_be_disjoint(token: jwcrypto.jwe.JWE):
    obj = json.loads(token.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'protected': b64encode(str.encode(json.dumps({'alg': 'foo'}))),
        'unprotected': {'alg': 'foo'},
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_protected_and_recipient_header_must_be_disjoint(token: jwcrypto.jwe.JWE):
    obj = json.loads(token.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'protected': b64encode(str.encode(json.dumps({'foo': 1}))),
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_unprotected_and_recipient_header_must_be_disjoint(token: jwcrypto.jwe.JWE):
    obj = json.loads(token.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'unprotected': {'bar': 2}
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_header_attribute_contains_merged(token: jwcrypto.jwe.JWE):
    obj = json.loads(token.serialize())
    obj.update({
        'unprotected': {'baz': 2}
    })
    jwe = JSONWebEncryption.parse_obj(obj)
    assert 'baz' in jwe.header


def test_flattened_protected_and_unprotected_header_must_be_disjoint(token_single: jwcrypto.jwe.JWE):
    obj = json.loads(token_single.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'protected': b64encode(str.encode(json.dumps({'alg': 'foo'}))),
        'unprotected': {'alg': 'foo'},
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_flattened_protected_and_recipient_header_must_be_disjoint(token_single: jwcrypto.jwe.JWE):
    obj = json.loads(token_single.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'header': {'bar': 1},
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_flattened_unprotected_and_recipient_header_must_be_disjoint(token_single: jwcrypto.jwe.JWE):
    obj = json.loads(token_single.serialize())
    JSONWebEncryption.parse_obj(obj)
    obj.update({
        'header': {'bar': 2}
    })
    with pytest.raises(pydantic.ValidationError):
        JSONWebEncryption.parse_obj(obj)


def test_parse_compact():
    payload = b'Hello world!'
    jwk = jwcrypto.jwk.JWK.generate(kty='oct', size=256)
    jwe = jwcrypto.jwe.JWE(
        payload,
        json_encode({
            'alg': "A256KW",
            'enc': "A256CBC-HS512"
        })
    )
    jwe.add_recipient(jwk)
    obj = JSONWebEncryption.parse_compact(
        str.encode(jwe.serialize(compact=True))
    )