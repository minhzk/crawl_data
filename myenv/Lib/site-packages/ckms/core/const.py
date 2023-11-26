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

DEFAULT_CONTENT_ENCRYPTION_ALGORITHM: str = 'A256GCM'

DEFAULT_EC_ENCRYPTION_ALGORITHM: str = 'ECDH-ES+A256KW'

DEFAULT_EC_ENCRYPTION_CURVE: str = 'P-256K'

DEFAULT_EC_SIGNING_ALGORITHM: str = 'ES384'

DEFAULT_EC_SIGNING_CURVE: str = 'P-384'

DEFAULT_ED_ENCRYPTION_ALGORITHM: str = 'ECDH-ES+A256KW'

DEFAULT_ED_ENCRYPTION_CURVE: str = 'X448'

DEFAULT_ED_SIGNING_CURVE: str = 'Ed448'

DEFAULT_RSA_ENCRYPTION_ALG: str = 'RSA-OAEP-256'

DEFAULT_RSA_SIGNING_ALG: str = 'PS256'

DEFAULT_SYMMETRIC_ENCRYPTION_ALGORITHM: str = 'A256GCMKW'

DEFAULT_SYMMETRIC_SIGNING_ALGORITHM: str = 'HS256'

DH_ALGORITHMS: set[str] = {
    'ECDH-ES',
    'ECDH-ES+A128KW',
    'ECDH-ES+A192KW',
    'ECDH-ES+A256KW',
}

ENCRYPTION_ALGORITHMS: set[str] = {
    #'A128CBC',
    #'A192CBC',
    #'A256CBC',
    'A128GCM',
    'A192GCM',
    'A256GCM',
}

KEYWRAP_ALGORITHMS: set[str] = {
    'A128KW',
    'A192KW',
    'A256KW',
    'A128GCMKW',
    'A192GCMKW',
    'A256GCMKW',
    'RSA1_5',
    'RSA-OAEP',
    'RSA-OAEP-256',
    'RSA-OAEP-384',
    'RSA-OAEP-512',
}

SIGNING_ALGORITHMS: set[str] = {
    'EdDSA',
    'ES256',
    'ES384',
    'ES512',
    'ES256K',
    'HS256',
    'HS384',
    'HS512',
    'RS256',
    'RS384',
    'RS512',
    'PS256',
    'PS384',
    'PS512',
}

ALGORITHMS: set[str] = DH_ALGORITHMS|ENCRYPTION_ALGORITHMS|KEYWRAP_ALGORITHMS|SIGNING_ALGORITHMS

ASYMMETRIC_SIGNING_ALGORITHMS: set[str] = {
    'EdDSA',
    'ES256',
    'ES384',
    'ES512',
    'ES256K',
    'RS256',
    'RS384',
    'RS512',
    'PS256',
    'PS384',
    'PS512',
}

ASYMMETRIC_ALGORITHMS: set[str] = {
    *ASYMMETRIC_SIGNING_ALGORITHMS,
    'ECDH-ES',
    'ECDH-ES+A128KW',
    'ECDH-ES+A192KW',
    'ECDH-ES+A256KW',
    'RSA1_5',
    'RSA-OAEP',
    'RSA-OAEP-256',
    'RSA-OAEP-384',
    'RSA-OAEP-512',
}

SYMMETRIC_ALGORITHMS: set[str] = ALGORITHMS - ASYMMETRIC_ALGORITHMS