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
from typing import Any

from .base import Algorithm
from .nullalgorithm import NullAlgorithm


__all__: list[str] = [
    'register',
    'Algorithm',
    'NullAlgorithm'
]


def alias(name: str, alias_of: str) -> None:
    """Create an alias of a cryptographic algorithm."""
    return Algorithm.alias(name, alias_of)


def register(name: str, base: type[Algorithm], params: Any) -> None:
    """Register a new algorithm preset using the given class."""
    return Algorithm.register(name, base=base, **params)


register('null', NullAlgorithm, {})
register('EdDSA', Algorithm, {
    'kty': 'OKP',
    'use': 'sig',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256K', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256K',
    'digest': 'sha256',
    'digest_oid': '1.2.840.10045.4.3.2',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256K-384', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256K',
    'digest': 'sha384',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256K-512', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256K',
    'digest': 'sha512',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256',
    'digest': 'sha256',
    'digest_oid': '1.2.840.10045.4.3.2',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256-384', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256',
    'digest': 'sha384',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES256-512', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-256',
    'digest': 'sha512',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES384-256', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-384',
    'digest': 'sha256',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES384', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-384',
    'digest': 'sha384',
    'digest_oid': '1.2.840.10045.4.3.3',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES384-512', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-384',
    'digest': 'sha512',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES512-256', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-521',
    'digest': 'sha256',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES512-384', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-521',
    'digest': 'sha384',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('ES512', Algorithm, {
    'kty': 'EC',
    'use': 'sig',
    'crv': 'P-521',
    'digest': 'sha512',
    'digest_oid': '1.2.840.10045.4.3.4',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('HS256', Algorithm, {
    'kty': 'oct',
    'use': 'sig',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('HS384', Algorithm, {
    'kty': 'oct',
    'use': 'sig',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'},
    'default': True
})

register('HS512', Algorithm, {
    'kty': 'oct',
    'use': 'sig',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('PS256', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PSS',
    'digest': 'sha256',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('PS384', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PSS',
    'digest': 'sha384',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'},
    'default': True
})

register('PS512', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PSS',
    'digest': 'sha512',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('RS256', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PKCSv1',
    'digest': 'sha256',
    'digest_oid': '1.2.840.113549.1.1.11',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('RS384', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PKCSv1',
    'digest': 'sha384',
    'digest_oid': '1.2.840.113549.1.1.12',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('RS512', Algorithm, {
    'kty': 'RSA',
    'use': 'sig',
    'padding': 'PKCSv1',
    'digest': 'sha512',
    'digest_oid': '1.2.840.113549.1.1.13',
    'allowed_ops': {'sign'},
    'default_ops': {'sign'}
})

register('A128GCM', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'decrypt', 'encrypt'},
    'default_ops': {'decrypt', 'encrypt'}
})

register('A192GCM', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'decrypt', 'encrypt'},
    'default_ops': {'decrypt', 'encrypt'}
})

register('A256GCM', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'decrypt', 'encrypt'},
    'default_ops': {'decrypt', 'encrypt'}
})

register('A128KW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+RFC3394',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'}
})

register('A192KW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+RFC3394',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'}
})

register('A256KW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+RFC3394',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'}
})

register('A128GCMKW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'}
})

register('A192GCMKW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'}
})

register('A256GCMKW', Algorithm, {
    'kty': 'oct',
    'use': 'enc',
    'mode': 'AES+GCM',
    'allowed_ops': {'unwrapKey', 'wrapKey'},
    'default_ops': {'unwrapKey', 'wrapKey'},
    'default': True
})

register('ECDH-ES', Algorithm, {
    'kty': 'OKP',
    'use': 'enc',
    'allowed_ops': {'deriveKey'},
    'default_ops': {'deriveKey'}
})

register('ECDH-ES+A128KW', Algorithm, {
    'kty': 'OKP',
    'use': 'enc',
    'allowed_ops': {'deriveKey'},
    'default_ops': {'deriveKey'}
})

register('ECDH-ES+A192KW', Algorithm, {
    'kty': 'OKP',
    'use': 'enc',
    'allowed_ops': {'deriveKey'},
    'default_ops': {'deriveKey'}
})

register('ECDH-ES+A256KW', Algorithm, {
    'kty': 'OKP',
    'use': 'enc',
    'allowed_ops': {'deriveKey'},
    'default_ops': {'deriveKey'},
    'default': True
})

register('RSA1_5', Algorithm, {
    'kty': 'RSA',
    'use': 'enc',
    'padding': 'PKCSv1',
    'digest': 'sha1',
    'allowed_ops': {'unwrapKey', 'decrypt'},
    'default_ops': {'unwrapKey'}
})

register('RSA-OAEP', Algorithm, {
    'kty': 'RSA',
    'use': 'enc',
    'padding': 'OAEP',
    'digest': 'sha1',
    'allowed_ops': {'unwrapKey', 'decrypt'},
    'default_ops': {'unwrapKey'}
})

register('RSA-OAEP-256', Algorithm, {
    'kty': 'RSA',
    'use': 'enc',
    'padding': 'OAEP',
    'digest': 'sha256',
    'allowed_ops': {'unwrapKey', 'decrypt'},
    'default_ops': {'unwrapKey'}
})

register('RSA-OAEP-384', Algorithm, {
    'kty': 'RSA',
    'use': 'enc',
    'padding': 'OAEP',
    'digest': 'sha384',
    'allowed_ops': {'unwrapKey', 'decrypt'},
    'default_ops': {'unwrapKey'},
    'default': True
})

register('RSA-OAEP-512', Algorithm, {
    'kty': 'RSA',
    'use': 'enc',
    'padding': 'OAEP',
    'digest': 'sha512',
    'allowed_ops': {'unwrapKey', 'decrypt'},
    'default_ops': {'unwrapKey'}
})