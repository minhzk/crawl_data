# pylint: skip-file
import pytest

import ckms


PROJECT = "unimatrixdev"

LOCATION = "europe-west4"

KEYRING = "local"


SIGNING_ALGORITHMS = [
    ('rsa_pkcs_2048', 'RS256'),
    ('rsa_pkcs_3072', 'RS256'),
    ('rsa_pkcs_4096', 'RS256'),
    ('rsa_pkcs_4096_sha512', 'RS512'),
    ('rsa_pss_2048', 'PS256'),
    ('rsa_pss_3072', 'PS256'),
    ('rsa_pss_4096', 'PS256'),
    ('rsa_pss_4096_sha512', 'PS512'),
    ('hmacsha256', 'HS256'),
    ('p256', 'ES256'),
    ('p384', 'ES384'),
    ('p256k', 'ES256K'),
]


@pytest.fixture(scope='session')
def keychain():
    return ckms.Keychain()


@pytest.fixture(scope='session')
def keyconfig():
    return {
        'p256': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "ec_sign_p256_sha256"
        },
        'p384': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "ec_sign_p384_sha384"
        },
        'p256k': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "ec_sign_secp256k1_sha256"
        },
        'hmacsha256': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "hmac_sha256"
        },
        'rsa_pkcs_2048': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pkcs1_2048_sha256"
        },
        'rsa_pkcs_3072': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pkcs1_3072_sha256"
        },
        'rsa_pkcs_4096': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pkcs1_4096_sha256"
        },
        'rsa_pkcs_4096_sha512': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pkcs1_4096_sha512"
        },
        'rsa_pss_2048': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pss_2048_sha256"
        },
        'rsa_pss_3072': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pss_3072_sha256"
        },
        'rsa_pss_4096': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pss_4096_sha256"
        },
        'rsa_pss_4096_sha512': {
            'provider': "google",
            'project': PROJECT,
            'location': LOCATION,
            'keyring': KEYRING,
            'key': "rsa_sign_pss_4096_sha512"
        },
    }
