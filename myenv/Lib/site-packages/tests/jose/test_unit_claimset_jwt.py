# pylint: skip-file
import time
from typing import Any

import pytest

from ckms.utils import b64encode
from ckms.types import ClaimSet
from ckms.types import ClaimTypeError
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload
from ckms.types import MaximumAgeExceeded
from ckms.types import MissingRequiredClaim
from ckms.types import TokenExpired
from ckms.types import TokenNotEffective
from ckms.types import WrongAudience


@pytest.mark.parametrize("claim", [
    "jti",
    "iss",
    "aud",
    "iat",
    "nbf",
    "exp"
])
def test_strict(claim: str):
    claims = JSONWebToken.strict(
        iss="foo",
        aud="foo",
        ttl=600
    )
    assert getattr(claims, claim, None) is not None


def test_strict_sets_standardized_claim():
    claims = JSONWebToken.strict(
        iss="foo",
        aud="foo",
        ttl=600,
        sub="foo"
    )
    assert claims.sub == "foo" # type: ignore


def test_strict_sets_private_claim():
    claims = JSONWebToken.strict(
        iss="foo",
        aud="foo",
        ttl=600,
        foo="foo"
    )
    assert claims.extra['foo'] == "foo"


def test_dict_only_returns_present_claims():
    claims = JSONWebToken(foo=1) # type: ignore
    data = claims.dict()
    assert len(data) == 1
    assert 'foo' in data


def test_json_only_returns_present_claims():
    claims = JSONWebToken(foo=1) # type: ignore
    data = claims.json()
    assert data == '{"foo": 1}'


def test_get_attribute():
    claims = JSONWebToken(foo=1) # type: ignore
    assert claims.extra['foo'] == 1


def test_strict_sets_ttl():
    claims = JSONWebToken.strict(
        iss="foo",
        aud="foo",
        ttl=600
    )
    assert claims.expires_in() == 600 # type: ignore
    time.sleep(1)
    assert claims.expires_in() == 599 # type: ignore


def test_serialize():
    claims = JSONWebToken.frompayload(bytes(JSONWebToken(iss='foo')))
    assert claims.iss == 'foo' # type: ignore


def test_frompayload():
    claims = JSONWebToken.frompayload(b64encode(b'{"foo": 1}'))
    assert claims.extra.get('foo') == 1


def test_frompayload_raised_malformed():
    with pytest.raises(MalformedPayload):
        JSONWebToken.frompayload(b'f')


@pytest.mark.parametrize("Model", [JSONWebToken])
@pytest.mark.parametrize("claim,value", [
    ('exp', 'a'),
    ('iat', 'a'),
    ('nbf', 'a'),
])
def test_invalid_type_raises_invalidclaimtype(
    Model: type[ClaimSet],
    claim: str,
    value: Any
):
    with pytest.raises(ClaimTypeError):
        Model.parse_obj({claim: value})


def test_verify_raises_missing_required_claim():
    claims = JSONWebToken(foo=1) # type: ignore
    with pytest.raises(MissingRequiredClaim):
        claims.verify(required={'bar'})
    claims.verify(required={'foo'})


def test_validate_exp_raises():
    claims = JSONWebToken(exp=1)
    with pytest.raises(TokenExpired):
        claims.verify(now=2)


def test_exp_from_expires_in():
    claims = JSONWebToken()
    assert claims.expires_in(ttl=5, now=0) == 5
    assert claims.exp == 5


def test_validate_nbf_raises():
    claims = JSONWebToken(nbf=2)
    with pytest.raises(TokenNotEffective):
        claims.verify(now=1)


def test_aud_is_set_when_not_provided():
    claims = JSONWebToken()
    assert isinstance(claims.aud, set)


def test_aud_is_set_when_string():
    claims = JSONWebToken(aud="foo") # type: ignore
    assert isinstance(claims.aud, set)
    assert claims.aud == {"foo"}


def test_aud_is_set_when_list():
    claims = JSONWebToken(aud=["foo", "bar"]) # type: ignore
    assert isinstance(claims.aud, set)
    assert claims.aud == {"foo", "bar"}


def test_aud_not_list_or_str_raises():
    with pytest.raises(ClaimTypeError):
        JSONWebToken(aud=1) # type: ignore


def test_aud_must_be_all_strings():
    with pytest.raises(ClaimTypeError):
        JSONWebToken(aud=[1, "foo"]) # type: ignore


def test_aud_must_intersect():
    claims = JSONWebToken(aud=["foo"]) # type: ignore
    with pytest.raises(WrongAudience):
        claims.verify(audience={"bar"})
    claims.verify(audience={"foo", "bar"})


def test_verify_strict():
    with pytest.raises(MissingRequiredClaim):
        claims = JSONWebToken(iat=5, exp=10)
        claims.verify(strict=True, now=9)


def test_verify_max_age_exceeded():
    claims = JSONWebToken(iat=1)
    with pytest.raises(MaximumAgeExceeded):
        claims.verify(max_age=1, now=3)


def test_verify_max_age():
    claims = JSONWebToken(iat=1)
    claims.verify(max_age=2, now=2)


def test_selfsigned():
    claims = JSONWebToken(sub='foo', iss='foo')
    assert claims.is_selfsigned()