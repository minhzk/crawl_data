# pylint: skip-file
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

import pydantic
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from google.cloud.kms import KeyManagementServiceAsyncClient

from ckms.core.models import KeySpecification
from ckms.types import Algorithm
from ckms.types import CryptographyPublicKeyType
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import AESAlgorithmType
from ckms.types import EllipticCurveAlgorithmType
from ckms.types import HMACAlgorithmType
from ckms.types import KeyAlgorithmType
from ckms.types import KeyUseType
from ckms.types import RSAAlgorithmType
from .igoogleprovider import IGoogleProvider


ALGORITHM_MAP: dict[str, tuple[KeyAlgorithmType, str, KeyUseType]] = {
    'EC_SIGN_SECP256K1_SHA256'      : (EllipticCurveAlgorithmType.ES256K, 'EC', KeyUseType.sign),
    'EC_SIGN_P256_SHA256'           : (EllipticCurveAlgorithmType.ES256, 'EC', KeyUseType.sign),
    'EC_SIGN_P384_SHA384'           : (EllipticCurveAlgorithmType.ES384, 'EC', KeyUseType.sign),
    'RSA_DECRYPT_OAEP_2048_SHA1'    : (RSAAlgorithmType.RSA_OAEP, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_2048_SHA256'  : (RSAAlgorithmType.RSA_OAEP256, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_3072_SHA1'    : (RSAAlgorithmType.RSA_OAEP, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_3072_SHA256'  : (RSAAlgorithmType.RSA_OAEP256, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_4096_SHA1'    : (RSAAlgorithmType.RSA_OAEP, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_4096_SHA256'  : (RSAAlgorithmType.RSA_OAEP256, 'RSA', KeyUseType.encrypt),
    'RSA_DECRYPT_OAEP_4096_SHA512'  : (RSAAlgorithmType.RSA_OAEP512, 'RSA', KeyUseType.encrypt),
    'RSA_SIGN_PSS_2048_SHA256'      : (RSAAlgorithmType.PS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PSS_3072_SHA256'      : (RSAAlgorithmType.PS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PSS_4096_SHA256'      : (RSAAlgorithmType.PS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PSS_4096_SHA512'      : (RSAAlgorithmType.PS512, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PKCS1_2048_SHA256'    : (RSAAlgorithmType.RS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PKCS1_3072_SHA256'    : (RSAAlgorithmType.RS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PKCS1_4096_SHA256'    : (RSAAlgorithmType.RS256, 'RSA', KeyUseType.sign),
    'RSA_SIGN_PKCS1_4096_SHA512'    : (RSAAlgorithmType.RS512, 'RSA', KeyUseType.sign),
    'HMAC_SHA256'                   : (HMACAlgorithmType.HS256, 'oct', KeyUseType.sign),
    'GOOGLE_SYMMETRIC_ENCRYPTION'   : (AESAlgorithmType.A256GCM, 'oct', KeyUseType.encrypt),
}


class GoogleKeySpecification(KeySpecification):
    kty: str = 'none'
    algorithm: Algorithm | None
    use: KeyUseType | None
    project: str | None
    location: str
    keyring: str = pydantic.Field(..., alias='key_ring')
    key: str = pydantic.Field(..., alias='crypto_key')
    version: int
    public: CryptographyPublicKeyType | None

    @property
    def crypto_key(self) -> str:
        return KeyManagementServiceAsyncClient.crypto_key_path(
            project=self.project,
            location=self.location,
            key_ring=self.keyring,
            crypto_key=self.key
        )

    @property
    def resource_name(self) -> str:
        return KeyManagementServiceAsyncClient.crypto_key_version_path(
            project=self.project,
            location=self.location,
            key_ring=self.keyring,
            crypto_key=self.key,
            crypto_key_version=self.version
        )

    @classmethod
    def autodiscover(
        cls,
        provider: IProvider,
        inspector: IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('project'): # pragma: no cover
            values['project'] = provider.project # type: ignore

    async def load(self) -> 'GoogleKeySpecification':
        provider: IGoogleProvider = self.provider # type: ignore
        inspector: IKeyInspector = provider.inspector
        async with provider.client() as client:
            name = self.resource_name
            version = await client.get_crypto_key_version( # type: ignore
                request={'name': name},
                timeout=5.0
            )
            if version.algorithm.name in ALGORITHM_MAP:
                algorithm, self.kty, self.use = ALGORITHM_MAP[version.algorithm.name] # type: ignore
                self.algorithm = Algorithm.get(algorithm.value) # type: ignore
                self.allow = {self.algorithm}
            else:
                raise NotImplementedError(version)
            self.curve = inspector.get_algorithm_curve(self.algorithm)

            # Normally, the kid is generated from the k value of the JWK,
            # but we have no access so use the resource name in Google
            # Cloud KMS.
            if self.is_symmetric():
                self.kid = provider.get_key_identifier(name)

            # Fetch public key for asymmetric types.
            if self.is_asymmetric():
                public = await client.get_public_key( # type: ignore
                    request={'name': name},
                    timeout=5.0
                )
                self.public = load_pem_public_key(public.pem.encode()) # type: ignore
                self.kid = self.provider.inspector.calculate_kid(self.public)

        self.loaded = True
        return self

    def get_public_key(self) -> CryptographyPublicKeyType | None:
        return self.public

    def has_key_material(self) -> bool:
        return False

    def __hash__(self) -> int: # type: ignore
        return self.resource_name.__hash__()