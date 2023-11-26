# pylint: skip-file
import os
import typing

import pytest
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import rsa

from ckms.core import KeyInspector


ASYMMETRIC_KEYS: list[typing.Any] = [
    ec.generate_private_key(curve=ec.SECP256R1()),
    ec.generate_private_key(curve=ec.SECP256R1()).public_key(),
    ed448.Ed448PrivateKey.generate(),
    ed448.Ed448PrivateKey.generate().public_key(),
    ed25519.Ed25519PrivateKey.generate(),
    ed25519.Ed25519PrivateKey.generate().public_key(),
    x448.X448PrivateKey.generate(),
    x448.X448PrivateKey.generate().public_key(),
    x25519.X25519PrivateKey.generate(),
    x25519.X25519PrivateKey.generate().public_key(),
    rsa.generate_private_key(public_exponent=65537, key_size=1024),
    rsa.generate_private_key(public_exponent=65537, key_size=1024).public_key(),
]


@pytest.mark.parametrize("key", ASYMMETRIC_KEYS + [
    algorithms.AES(os.urandom(16)),
    algorithms.AES(os.urandom(24)),
    algorithms.AES(os.urandom(32)),
    'foo'
])
def test_keyinspector_supports_keytypes(key: KeyInspector.KeyType | str):
    inspector = KeyInspector()
    inspector.calculate_kid(key)


@pytest.mark.parametrize("key", [
    ec.generate_private_key(curve=ec.SECP256R1()),
    ed448.Ed448PrivateKey.generate(),
    ed25519.Ed25519PrivateKey.generate(),
    x448.X448PrivateKey.generate(),
    x25519.X25519PrivateKey.generate(),
    rsa.generate_private_key(public_exponent=65537, key_size=1024),
])
def test_private_kid_equals_public_kid(key: KeyInspector.PrivateKeyType):
    inspector = KeyInspector()
    public = key.public_key()
    assert inspector.calculate_kid(key) == inspector.calculate_kid(public)


@pytest.mark.parametrize("key", ASYMMETRIC_KEYS)
def test_to_pem(key: KeyInspector.KeyType):
    inspector = KeyInspector()
    pem = inspector.to_pem(key)
    assert isinstance(pem, bytes)

@pytest.mark.parametrize("key", ASYMMETRIC_KEYS + [
    algorithms.AES(os.urandom(16)),
    algorithms.AES(os.urandom(24)),
    algorithms.AES(os.urandom(32)),
    os.urandom(64)
])
def test_to_jwk(key: KeyInspector.KeyType | bytes):
    inspector = KeyInspector()
    inspector.to_jwk(key)


@pytest.mark.parametrize("key", ASYMMETRIC_KEYS + [
    algorithms.AES(os.urandom(16)),
    algorithms.AES(os.urandom(24)),
    algorithms.AES(os.urandom(32)),
    os.urandom(64)
])
def test_from_jwk(key: KeyInspector.KeyType | bytes):
    inspector = KeyInspector()
    decoded = inspector.from_jwk(
        typing.cast(dict[str, str], inspector.to_jwk(key))
    )

    assert inspector.calculate_kid(decoded) == inspector.calculate_kid(key)
    if isinstance(key, algorithms.AES):
        key = key.key
    assert type(key) == type(decoded)