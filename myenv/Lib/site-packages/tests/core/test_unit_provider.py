# pylint: skip-file
from typing import cast
from typing import Any

import pytest

from ckms import core
from ckms.core.local import LocalProvider
from ckms.core.random import RandomProvider


RSA_SIGNING_ALGORITHMS: list[str] = [
    'RS256',
    'RS384',
    'RS512',
    'PS256',
    'PS384',
    'PS512',
]

RSA_ENCRYPTION_ALGORITHMS: list[str] = [
    'RSA-OAEP',
    'RSA-OAEP-256',
    'RSA-OAEP-384',
    'RSA-OAEP-512',
]

EC_SIGNING_ALGORITHMS: list[str] = [
    'ES256',
    'ES384',
    'ES512',
    'ES256K',
]

ECDH_ENCRYPTION_ALGORITHMS: list[str] = [
    'ECDH-ES',
    'ECDH-ES+A128KW',
    'ECDH-ES+A192KW',
    'ECDH-ES+A256KW',
]

SYMMETRIC_ENCRYPTION_ALGORITHMS: list[str] = [
    'A128KW',
    'A192KW',
    'A256KW',
    'A128GCMKW',
    'A192GCMKW',
    'A256GCMKW',
]

HMAC_SIGNING_ALGORITHMS: list[str] = ['HS256', 'HS384', 'HS512']

OKP_SIGNING_CURVES: list[str] = ['Ed448', 'Ed25519']

OKP_ENCRYPTION_CURVES: list[str] = ['X448', 'X25519']

SUPPORTED_KEYS: list[dict[str, Any]] = [
    {
        'key': {'path': 'pki/rsa.key'}
    }
]


@pytest.fixture
def provider() -> LocalProvider:
    return cast(LocalProvider, core.provider('local'))


@pytest.mark.parametrize("algorithm", RSA_SIGNING_ALGORITHMS)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_rsa_signing(
    provider: LocalProvider,
    algorithm: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'RSA',
        'algorithm': algorithm,
        'provider': 'local'
    })
    assert spec.kty == 'RSA'
    assert spec.use == 'sig'
    assert spec.algorithm == algorithm


@pytest.mark.parametrize("algorithm", RSA_ENCRYPTION_ALGORITHMS)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_rsa_encryption(
    provider: LocalProvider,
    algorithm: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'RSA',
        'algorithm': algorithm,
        'provider': 'local'
    })
    assert spec.kty == 'RSA'
    assert spec.use == 'enc'
    assert spec.algorithm == algorithm


@pytest.mark.parametrize("algorithm", EC_SIGNING_ALGORITHMS)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_ec_signing(
    provider: LocalProvider,
    algorithm: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'EC',
        'algorithm': algorithm,
        'provider': 'local'
    })
    assert spec.kty == 'EC'
    assert spec.use == 'sig'
    assert spec.algorithm == algorithm


@pytest.mark.parametrize("algorithm", HMAC_SIGNING_ALGORITHMS)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_symmetric_sign(
    provider: LocalProvider,
    algorithm: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'oct',
        'algorithm': algorithm,
        'provider': 'local'
    })
    assert spec.kty == 'oct'
    assert spec.use == 'sig'
    assert spec.algorithm == algorithm


@pytest.mark.parametrize("algorithm", SYMMETRIC_ENCRYPTION_ALGORITHMS)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_symmetric_encrypt(
    provider: LocalProvider,
    algorithm: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'oct',
        'algorithm': algorithm,
        'provider': 'local'
    })
    assert spec.kty == 'oct'
    assert spec.use == 'enc'
    assert spec.algorithm == algorithm


@pytest.mark.parametrize("curve", OKP_SIGNING_CURVES)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_okp_signing(
    provider: LocalProvider,
    curve: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'OKP',
        'curve': curve,
        'provider': 'local'
    })
    assert spec.kty == 'OKP'
    assert spec.use == 'sig'
    assert spec.algorithm == "EdDSA"
    assert spec.curve == curve


@pytest.mark.parametrize("curve", OKP_ENCRYPTION_CURVES)
@pytest.mark.parametrize("params", SUPPORTED_KEYS)
def test_validate_spec_okp_encryption(
    provider: LocalProvider,
    curve: str,
    params: dict[str, Any]
):
    spec = provider.parse_spec({
        **params,
        'kty': 'OKP',
        'curve': curve,
        'provider': 'local'
    })
    assert spec.kty == 'OKP'
    assert spec.use == 'enc'
    assert spec.algorithm == "ECDH-ES+A256KW"


@pytest.mark.parametrize("name,cls", [
    ("local", LocalProvider),
    ("random", RandomProvider),
])
def test_lookup_default_providers(name: str, cls: type[core.Provider]):
    provider = core.provider(name)
    assert isinstance(provider, cls)


@pytest.mark.parametrize("name", [
    "local"
])
@pytest.mark.asyncio
async def test_provider_supports_random(name: str):
    provider = core.provider(name)
    assert len(await provider.random(16)) == 16
    assert isinstance(await provider.random_urlsafe(16), str)