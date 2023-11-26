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
from typing import cast
from typing import Any
from typing import Awaitable
from typing import Callable

import crcmod
import google.auth
from google.api_core.exceptions import InvalidArgument
from google.auth.credentials import Credentials
from google.cloud.kms import AsymmetricDecryptResponse
from google.cloud.kms import DecryptResponse
from google.cloud.kms import KeyManagementServiceAsyncClient
from google.cloud.secretmanager import SecretManagerServiceAsyncClient

from ckms import core
from ckms.lib import dsnparse
from ckms.utils import normalize_ec_signature
from ckms.types import AESOperation
from ckms.types import CipherText
from ckms.types import EllipticCurveOperation
from ckms.types import HMACOperation
from ckms.types import RSAOperation
from ckms.types import SigningOperation
from .types import GoogleKeySpecification
from .types import IGoogleProvider
from .types import SecretManagerBlob


class GoogleProvider(IGoogleProvider):
    __module__: str = 'ckms.ext.google'
    credentials: Credentials
    project: str
    spec: type[GoogleKeySpecification] = GoogleKeySpecification
    timeout: int = 10.0

    @staticmethod
    def crc32c(data: bytes) -> int:
        """Calculates the CRC32C checksum of the provided data."""
        func = crcmod.predefined.mkPredefinedCrcFun('crc-32c')
        return func(data)

    def client(self) -> KeyManagementServiceAsyncClient:
        return KeyManagementServiceAsyncClient(credentials=self.credentials)

    def get_key_identifier(self, key: Any) -> str:
        return self.inspector.calculate_kid(key)

    def on_init(self):
        self.credentials, self.project = cast(Credentials, google.auth.default())

    def parse_dsn(self, dsn: dsnparse.ParseResult) -> dict[str, Any]:
        if dsn.host != "cloudkms.googleapis.com":
            raise ValueError(f"Invalid service: %s", dsn.host)
        return {
            **dsn.query_params,
            **KeyManagementServiceAsyncClient.parse_crypto_key_path(dsn.path[1:]),
            'provider': 'google'
        }

    async def decrypt_aes(self, op: AESOperation) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        async with self.client() as client:
            return await self.decrypt_remote(op, client.decrypt, spec.crypto_key)

    async def decrypt_remote(
        self,
        op: AESOperation | RSAOperation,
        func: Callable[..., Awaitable[AsymmetricDecryptResponse | DecryptResponse]],
        using: str
    ) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        ct = await op.get_message()
        request = {
            'name': using,
            'ciphertext': ct,
            'ciphertext_crc32c': self.crc32c(ct)
        }
        if op.aad is not None:
            assert spec.is_aead()
            request.update({
                'additional_authenticated_data': op.aad,
                'additional_authenticated_data_crc32c': self.crc32c(op.aad)
            })
        async with self.client() as client:
            try:
                response = await func(
                    request=request,
                    timeout=self.timeout
                )
            except InvalidArgument as exception:
                raise self.Undecryptable
            if not self.crc32c(response.plaintext) == response.plaintext_crc32c: # pragma: no cover
                raise ValueError("Corrupted plain text in transit.")

        return response.plaintext

    async def decrypt_rsa(self, op: RSAOperation) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        async with self.client() as client:
            return await self.decrypt_remote(op, client.asymmetric_decrypt, spec.resource_name)

    async def encrypt_aes(self, op: AESOperation) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        pt = await op.get_message()
        request = {
            'name': spec.resource_name,
            'plaintext': pt,
            'plaintext_crc32c': self.crc32c(pt)
        }
        assert spec.is_aead()
        if op.aad is not None:
            request.update({
                'additional_authenticated_data': op.aad,
                'additional_authenticated_data_crc32c': self.crc32c(op.aad)
            })
        async with self.client() as client:
            response = await client.encrypt(
                request=request,
                timeout=self.timeout
            )
            if not response.verified_plaintext_crc32c: # pragma: no cover
                raise ValueError("Plaintext checksum not considered or verified by cloud service.")
            if not response.verified_additional_authenticated_data_crc32c\
            and op.aad is not None: # pragma: no cover
                raise ValueError("AAD checksum not considered or verified by cloud service.")
            if not self.crc32c(response.ciphertext) == response.ciphertext_crc32c: # pragma: no cover
                raise ValueError("Corrupted cipher text in transit.")

        # Assume here that the Google Cloud KMS encryption key is never
        # used outside the HSM (i.e. if it was imported). Since tag/iv
        # values are expected, we fill them with zeroes here (TODO).
        return CipherText(
            aad=op.aad,
            buf=response.ciphertext,
            iv=b'0' * 12,
            tag=b'0' * 16
        )

    async def encrypt_rsa(self, op: RSAOperation) -> CipherText:
        p = self.get('local')
        return await p.encrypt_rsa(op)

    async def fetch(self, params: core.RemoteBlob) -> bytes: # pragma: no cover
        """Fetches the content of the remote blob using the parameters
        specified. Return a byte-string holding the content.
        """
        blob = SecretManagerBlob.parse_obj(params.dict())
        client = SecretManagerServiceAsyncClient(credentials=self.credentials)
        secret = client.secret_path(blob.project, blob.secret)
        async with client:
            response = await client.access_secret_version(
                request={
                    'name': f'{secret}/versions/{blob.version}'
                }
            )
        return response.payload.data

    async def sign_ec(self, op: EllipticCurveOperation) -> bytes:
        return await self.sign_asymmetric(op)

    async def sign_hmac(self, op: HMACOperation) -> bytes:
        return await self.sign_symmetric(op)

    async def sign_rsa(self, op: RSAOperation) -> bytes:
        return await self.sign_asymmetric(op)

    async def sign_symmetric(self, op: SigningOperation) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        data = await op.get_message()
        checksum = self.crc32c(data)
        request = {
            'name': spec.resource_name,
            'data': data,
            'data_crc32c': checksum
        }
        async with self.client() as client:
            response = await client.mac_sign(
                request=request,
                timeout=self.timeout
            )
            if not response.verified_data_crc32c: # pragma: no cover
                raise ValueError("Data checksum not considered or verified by cloud service.")
            if self.crc32c(response.mac) != response.mac_crc32c: # pragma: no cover
                raise ValueError("Corrupted MAC in transit.")
        return response.mac

    async def sign_asymmetric(self, op: SigningOperation) -> bytes:
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        public = spec.get_public_key()
        data = await op.get_digest()
        checksum = self.crc32c(data)
        digest = {op.digest: data}
        request = {
            'name': spec.resource_name,
            'digest': digest,
            'digest_crc32c': checksum
        }
        async with self.client() as client:
            response = await client.asymmetric_sign(
                request=request,
                timeout=self.timeout
            )
            crc = response.signature_crc32c
            if not response.verified_digest_crc32c: # pragma: no cover
                raise ValueError("Digest checksum not considered or verified by cloud service.")
            if crc != self.crc32c(response.signature): # pragma: no cover
                raise ValueError("Corrupted signature in transit.")

        sig = response.signature
        if spec.kty == "EC":
            sig = normalize_ec_signature(
                l=(public.curve.key_size + 7) // 8,
                sig=sig
            )
        return sig

    async def verify_hmac(self, op: HMACOperation) -> bool:
        if op.signature is None: # pragma: no cover
            raise ValueError("Signature can not be None.")
        if len(op.signature) != 32:
            return False
        spec = cast(GoogleKeySpecification, op.get_keyspec())
        data = await op.get_message()
        checksum = self.crc32c(data)
        request = {
            'name': spec.resource_name,
            'data': data,
            'data_crc32c': checksum,
            'mac': op.signature,
            'mac_crc32c': self.crc32c(op.signature)
        }
        async with self.client() as client:
            response = await client.mac_verify(
                request=request,
                timeout=self.timeout
            )
            if not response.verified_mac_crc32c: # pragma: no cover
                raise ValueError("HMAC checksum not considered or verified by cloud service.")
            if not response.verified_data_crc32c: # pragma: no cover
                raise ValueError("Data checksum not considered or verified by cloud service.")
        return response.success
