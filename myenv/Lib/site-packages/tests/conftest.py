# pylint: skip-file
import asyncio
import copy
import os
from typing import Any

import pytest
import pytest_asyncio

import ckms.core
from ckms.core import Keychain


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture
def data():
    return os.urandom(16)


@pytest.fixture(scope='session')
def keyconfig() -> dict[str, Any]:
    return {}


@pytest.fixture(scope='session')
def asymmetric_sig_keys() -> dict[str, Any]:
    return {
        'EdDSA': {
            'provider': 'local',
            'kty': 'OKP',
            'use': 'sig'
        },
        'ES256': {
            'provider': 'local',
            'kty': 'EC',
            'algorithm': 'ES256'
        },
        'ES256K': {
            'provider': 'local',
            'kty': 'EC',
            'algorithm': 'ES256K'
        },
        'ES384': {
            'provider': 'local',
            'kty': 'EC',
            'algorithm': 'ES384'
        },
        'ES512': {
            'provider': 'local',
            'kty': 'EC',
            'algorithm': 'ES512'
        },
        'RS256': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RS256',
            'key': {'path': 'pki/RS256.key'}
        },
        'RS384': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RS384',
            'key': {'path': 'pki/RS384.key'}
        },
        'RS512': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RS512',
            'key': {'path': 'pki/RS512.key'}
        },
        'PS256': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'PS256',
            'key': {'path': 'pki/PS256.key'}
        },
        'PS384': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'PS384',
            'key': {'path': 'pki/PS384.key'}
        },
        'PS512': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'PS512',
            'key': {'path': 'pki/PS512.key'}
        },
    }


@pytest.fixture(scope='session')
def asymmetric_enc_keys() -> dict[str, Any]:
    return {
        'ECDH-ES': {
            'provider': 'local',
            'kty': 'OKP',
            'algorithm': 'ECDH-ES',
            'use': 'enc'
        },
        'ECDH-ES+A128KW': {
            'provider': 'local',
            'kty': 'OKP',
            'algorithm': 'ECDH-ES+A128KW',
            'use': 'enc'
        },
        'ECDH-ES+A192KW': {
            'provider': 'local',
            'kty': 'OKP',
            'algorithm': 'ECDH-ES+A192KW',
            'use': 'enc'
        },
        'ECDH-ES+A256KW': {
            'provider': 'local',
            'kty': 'OKP',
            'algorithm': 'ECDH-ES+A256KW',
            'use': 'enc'
        },
        'RSA-OAEP': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA-OAEP',
            'key': {'path': 'pki/RSA-OAEP.key'}
        },
        'RSA-OAEP-256': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA-OAEP-256',
            'key': {'path': 'pki/RSA-OAEP-256.key'}
        },
        'RSA-OAEP-384': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA-OAEP-384',
            'key': {'path': 'pki/RSA-OAEP-384.key'}
        },
        'RSA-OAEP-512': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA-OAEP-512',
            'key': {'path': 'pki/RSA-OAEP-512.key'}
        },
        'RSA1_5': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA1_5',
            'key': {'path': 'pki/RSA1_5.key'}
        },
    }


@pytest.fixture(scope='session')
def symmetric_sig_keys() -> dict[str, Any]:
    return {
        'HS256': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS256',
            'key': {'length': 32}
        },
        'HS384': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS384',
            'key': {'length': 32}
        },
        'HS512': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'HS512',
            'key': {'length': 32}
        },
    }


@pytest.fixture(scope='session')
def symmetric_enc_keys() -> dict[str, Any]:
    return {
        'A128GCM': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A128GCM',
            'key': {'length': 16}
        },
        'A192GCM': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A192GCM',
            'key': {'length': 24}
        },
        'A256GCM': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A256GCM',
            'key': {'length': 32}
        },
        'A128GCMKW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A128GCMKW',
            'key': {'length': 16}
        },
        'A192GCMKW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A192GCMKW',
            'key': {'length': 24}
        },
        'A256GCMKW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A256GCMKW',
            'key': {'length': 32}
        },
        'A128KW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A128KW',
            'key': {'length': 16}
        },
        'A192KW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A192KW',
            'key': {'length': 24}
        },
        'A256KW': {
            'provider': 'local',
            'kty': 'oct',
            'algorithm': 'A256KW',
            'key': {'length': 32}
        },
    }


@pytest.fixture(scope='session')
def asymmetric_keys(
    asymmetric_sig_keys: dict[str, Any],
    asymmetric_enc_keys: dict[str, Any],
) -> dict[str, Any]:
    return {
        **asymmetric_sig_keys,
        **asymmetric_enc_keys
    }


@pytest.fixture(scope='session')
def symmetric_keys(
    symmetric_sig_keys: dict[str, Any],
    symmetric_enc_keys: dict[str, Any],
) -> dict[str, Any]:
    return {
        **symmetric_sig_keys,
        **symmetric_enc_keys
    }


@pytest.fixture(scope='session')
def keys(
    asymmetric_keys: dict[str, Any],
    symmetric_keys: dict[str, Any],
) -> dict[str, Any]:
    return {
        **asymmetric_keys,
        **symmetric_keys
    }


@pytest_asyncio.fixture(scope='session') # type: ignore
async def keychain(keys: dict[str, Any]):
    keychain = Keychain()
    keychain.configure(keys=copy.deepcopy(keys))
    await keychain
    return keychain


@pytest_asyncio.fixture(scope='session', autouse=True) # type: ignore
async def setup_keychain(keychain: Keychain):
    await keychain


@pytest_asyncio.fixture(scope='session') # type: ignore
async def hs256():
    key = ckms.core.parse_spec({
        'provider': 'local',
        'kty': 'oct',
        'algorithm': 'HS256',
        'key': {'length': 32}
    })
    await key
    return key


@pytest_asyncio.fixture(scope='session') # type: ignore
async def hs384():
    key = ckms.core.parse_spec({
        'provider': 'local',
        'kty': 'oct',
        'algorithm': 'HS384',
        'key': {'length': 32}
    })
    await key
    return key