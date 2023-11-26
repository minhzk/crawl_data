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
"""Declares :class:`Provider`."""
import functools
from typing import Any
from typing import Awaitable

from cryptography.hazmat.primitives.keywrap import aes_key_wrap

from ckms import types
from ckms.types import AESOperation
from ckms.types import AESKeywrapOperation
from ckms.types import CipherText
from ckms.types import EdDSAOperation
from ckms.types import EllipticCurveOperation
from ckms.types import HMACOperation
from ckms.types import IProvider
from ckms.types import JSONWebKey
from ckms.types import KeywrapOperation
from ckms.types import RSAOperation
from ckms.types import SigningOperation
from ckms.core.models import KeySpecification
from ckms.utils import b64encode
from ..keyinspector import KeyInspector


class Provider(IProvider):
    __module__: str = 'ckms.core'
    algorithm_operations: dict[str, Any] = {
        'A128KW'        : AESKeywrapOperation,
        'A192KW'        : AESKeywrapOperation,
        'A256KW'        : AESKeywrapOperation,
        'A128GCM'       : AESOperation,
        'A192GCM'       : AESOperation,
        'A256GCM'       : AESOperation,
        'A128GCMKW'     : AESOperation,
        'A192GCMKW'     : AESOperation,
        'A256GCMKW'     : AESOperation,
        'EdDSA'         : EdDSAOperation,
        'ES256'         : EllipticCurveOperation,
        'ES384'         : EllipticCurveOperation,
        'ES512'         : EllipticCurveOperation,
        'ES256K'        : EllipticCurveOperation,
        'HS256'         : HMACOperation,
        'HS384'         : HMACOperation,
        'HS512'         : HMACOperation,
        'PS256'         : RSAOperation,
        'PS384'         : RSAOperation,
        'PS512'         : RSAOperation,
        'RS256'         : RSAOperation,
        'RS384'         : RSAOperation,
        'RS512'         : RSAOperation,
        'RSA1_5'        : RSAOperation,
        'RSA-OAEP'      : RSAOperation,
        'RSA-OAEP-256'  : RSAOperation,
        'RSA-OAEP-384'  : RSAOperation,
        'RSA-OAEP-512'  : RSAOperation,
    }
    inspector: KeyInspector
    name: str
    spec: type[KeySpecification]

    def __init__(
        self,
        inspector: KeyInspector | None = None
    ):
        self._providers = Provider._providers
        self.inspector = inspector or KeyInspector()
        self.on_init()

    def jwk(self, spec: KeySpecification, private: bool, **claims: Any) -> JSONWebKey:
        key = spec.get_public_key() if not private else spec.get_private_key()
        ops = spec.key_ops
        if not private:
            ops = spec.as_public().key_ops
        return JSONWebKey.parse_obj({
            **self.inspector.to_jwk(key),
            'kid': spec.kid,
            'kty': spec.kty,
            'alg': spec.algorithm,
            'key_ops': ops,
            **claims
        })

    def on_init(self) -> None:
        """Called when the :class:`Provider` is initialized."""
        pass

    def configure(self, **params: Any) -> None:
        """Configures the provider with the given parameters."""
        raise NotImplementedError

    def get_hashing_algorithm(self, algorithm: str) -> str | None:
        """Return a string indicating the hashing algorithm."""
        return self.inspector.get_hashing_algorithm(algorithm)

    def parse_spec(self, spec: dict[str, Any]) -> KeySpecification:
        """Parse a key specification from a dictionary."""
        assert self.spec is not None # nosec
        return self.spec.parse_obj({
            **spec,
            'provider': self
        })

    async def fetch(self, blob: Any) -> bytes:
        """Fetches the content of the remote blob using the parameters
        specified. Return a byte-string holding the content.
        """
        raise NotImplementedError

    async def random(self, length: int) -> bytes:
        """Return a random byte-sequence of the given length."""
        random = self.get('random')
        return await random.random(length=length)

    async def random_urlsafe(self, length: int) -> str:
        """Like :meth:`random()`, but returs a Base64, URL-safe encoded
        string.
        """
        return bytes.decode(b64encode(await self.random(length)))

    def calculate_kid(self, value: Any) -> str:
        return self.inspector.calculate_kid(value)

    def decrypt(
        self,
        key: KeySpecification,
        algorithm: str,
        ciphertext: types.CipherText
    ) -> bytes | Awaitable[bytes]:
        op = self.algorithm_operations[algorithm].fromalgorithm(
            algorithm=algorithm,
            spec=key,
            content=ciphertext,
            aad=ciphertext.aad,
            iv=ciphertext.iv,
            tag=ciphertext.tag
        )
        return self._decrypt(op)

    @functools.singledispatchmethod
    def _decrypt(self, op: types.Operation) -> bytes | Awaitable[bytes]:
        raise NotImplementedError(
            f"Operation {type(op).__name__} is not implemented by "
            f"{type(self).__name__}."
        )

    @_decrypt.register
    def _decrypt_aes(self, op: types.AESOperation) -> bytes | Awaitable[bytes]:
        return self.decrypt_aes(op)

    @_decrypt.register
    def _decrypt_aes_wrap(self, op: types.AESKeywrapOperation) -> bytes | Awaitable[bytes]:
        return self._unwrap(op)

    def decrypt_aes(self, op: types.AESOperation) -> bytes | Awaitable[bytes]:
        """Decrypt a plain text using Advances Encryption Standard (AES)."""
        raise NotImplementedError(
            f"AES decryption is not supported by {type(self).__name__}"
        )

    @_decrypt.register
    def _decrypt_rsa(self, op: types.RSAOperation) -> bytes | Awaitable[bytes]:
        return self.decrypt_rsa(op)

    def decrypt_rsa(self, op: types.RSAOperation) -> bytes | Awaitable[bytes]:
        """Decrypt a plain text using RSA."""
        raise NotImplementedError(
            f"RSA decryption is not supported by {type(self).__name__}"
        )

    def encrypt(
        self,
        key: KeySpecification,
        algorithm: str,
        plaintext: types.PlainText,
        **kwargs: Any
    ) -> types.EncryptResult:
        """Encrypt the given message with the specified key."""
        op = self.algorithm_operations[algorithm].fromalgorithm(
            algorithm=algorithm,
            spec=key,
            content=plaintext,
            **kwargs
        )
        return self._encrypt(op)

    @functools.singledispatchmethod # type: ignore
    def _encrypt(
        self,
        op: types.Operation
    ) -> types.EncryptResult:
        raise NotImplementedError(
            f"Operation {type(op).__name__} is not implemented by "
            f"{type(self).__name__}."
        )

    @_encrypt.register
    def _encrypt_aes(self, op: types.AESOperation) -> types.EncryptResult:
        return self.encrypt_aes(op)

    @_encrypt.register
    def _encrypt_aes_wrap(self, op: types.AESKeywrapOperation) -> types.EncryptResult:
        return self._wrap(op)

    @_encrypt.register
    def _encrypt_rsa(self, op: types.RSAOperation) -> types.EncryptResult:
        return self.encrypt_rsa(op)

    def encrypt_aes(self, op: types.AESOperation) -> types.EncryptResult:
        """Encrypt a plain text using Advanced Encryption Standard (AES)."""
        raise NotImplementedError(
            f"AES encryption is not supported by {type(self).__name__}"
        )

    def encrypt_rsa(self, op: types.RSAOperation) -> types.EncryptResult:
        """Encrypt a plain text using RSA."""
        raise NotImplementedError(
            f"RSA encryption is not supported by {type(self).__name__}"
        )

    def unwrap(self, op: types.KeywrapOperation) -> bytes | Awaitable[bytes]:
        """Wrap a key using a symmetric encryption algorithm."""
        raise NotImplementedError(
            f"Key unwrapping is not supported by {type(self).__name__}"
        )

    @functools.singledispatchmethod
    def _unwrap(self, op: types.KeywrapOperation) -> bytes | Awaitable[bytes]:
        """Encrypt a plain text using RSA."""
        raise NotImplementedError(
            f"Key unwrapping is not supported by {type(self).__name__}"
        )

    @_unwrap.register
    def _unwrap_aes_wrap(self, op: types.AESKeywrapOperation) -> bytes | Awaitable[bytes]:
        return self.unwrap_aes_wrap(op)

    def unwrap_aes_wrap(self, op: types.AESKeywrapOperation) -> bytes | Awaitable[bytes]:
        """Unwrap a key using AES Key Wrapping."""
        raise NotImplementedError(
            f"AES key unwrapping is not supported by {type(self).__name__}"
        )

    def wrap(
        self,
        key: Any,
        algorithm: str,
        wrap: types.PlainText,
        **kwargs: Any
    ) -> Any | Awaitable[Any]:
        """Wrap key `wrap` using the given `key`."""
        op = self.algorithm_operations[algorithm].fromalgorithm(
            algorithm=algorithm,
            spec=key,
            content=wrap,
            **kwargs
        )
        func = self._wrap
        if not isinstance(op, (KeywrapOperation, AESKeywrapOperation)):
            func = self._encrypt
        return func(op)

    @functools.singledispatchmethod
    def _wrap(self, op: KeywrapOperation) -> types.EncryptResult:
        raise NotImplementedError(
            f"Operation {type(op).__name__} is not implemented by "
            f"{type(self).__name__}."
        )

    @_wrap.register
    def _wrap_aeskw_(self, op: AESKeywrapOperation) -> types.EncryptResult:
        spec = op.get_keyspec()
        return CipherText(
            buf=aes_key_wrap(
                wrapping_key=spec.get_private_bytes(),
                key_to_wrap=bytes(op.content)
            )
        )

    def sign(
        self,
        key: KeySpecification,
        algorithm: str,
        message: types.Digest | types.Message
    ) -> bytes | Awaitable[bytes]:
        """Sign the given digest or message with the specified key. Return
        a byte-sequence holding the signature.
        """
        op = self.algorithm_operations[algorithm].fromalgorithm(
            algorithm=algorithm,
            spec=key,
            content=message
        )
        return self._sign(op)

    @functools.singledispatchmethod # type: ignore
    def _sign(self, op: types.SigningOperation) -> IProvider.SignResult: # pragma: no cover
        raise NotImplementedError(
            f"Operation {type(op).__name__} is not implemented by "
            f"{type(self).__name__}."
        )

    @_sign.register
    def _sign_ec(self, op: EllipticCurveOperation) -> IProvider.SignResult: # pragma: no cover
        return self.sign_ec(op)

    @_sign.register
    def _sign_eddsa(self, op: EdDSAOperation) -> IProvider.SignResult: # pragma: no cover
        return self.sign_eddsa(op)

    @_sign.register
    def _sign_hmac(self, op: HMACOperation) -> IProvider.SignResult: # pragma: no cover
        return self.sign_hmac(op)

    @_sign.register
    def _sign_rsa(self, op: RSAOperation) -> IProvider.SignResult: # pragma: no cover
        return self.sign_rsa(op)

    def sign_ec(self, op: EllipticCurveOperation) -> IProvider.SignResult:
        """Create a digital signature using an elliptic curve private key."""
        raise NotImplementedError(
            f"Elliptic curve signing is not supported by {type(self).__name__}"
        )

    def sign_eddsa(self, op: EdDSAOperation) -> IProvider.SignResult:
        """Create a digital signature using an Ed448 or Ed25519 private key."""
        raise NotImplementedError(
            f"EdDSA signing is not supported by {type(self).__name__}"
        )

    def sign_hmac(self, op: HMACOperation) -> IProvider.SignResult:
        """Create a digital signature using a HMAC."""
        raise NotImplementedError(
            f"HMAC signing is not supported by {type(self).__name__}"
        )

    def sign_rsa(self, op: RSAOperation) -> IProvider.SignResult:
        """Create a digital signature using an RSA private key."""
        raise NotImplementedError(
            f"RSA signing is not supported by {type(self).__name__}"
        )

    def verify(
        self,
        key: KeySpecification,
        algorithm: str,
        message: types.Digest | types.Message,
        signature: bytes
    ) -> bool | Awaitable[bool]:
        """Verify a digital signature, specified by the operation."""
        op = self.algorithm_operations[algorithm].fromalgorithm(
            algorithm=algorithm,
            spec=key,
            content=message,
            signature=signature
        )
        return self._verify(op)

    @functools.singledispatchmethod # type: ignore
    def _verify(
        self,
        op: SigningOperation
    ) -> bool | Awaitable[bool]:
        raise NotImplementedError(
            f"Operation {type(op).__name__} is not implemented by "
            f"{type(self).__name__}."
        )

    def verify_ec(self, op: types.EllipticCurveOperation) -> bool | Awaitable[bool]:
        """Verify a digital signature that was created with an elliptic curve
        private key.
        """
        raise NotImplementedError(
            f"Elliptic curve verification is not supported by {type(self).__name__}"
        )

    def verify_eddsa(self, op: types.EdDSAOperation) -> bool | Awaitable[bool]:
        """Verify a digital signature that was created with an Ed448 or Ed25519
        private key.
        """
        raise NotImplementedError(
            f"EdDSA verification is not supported by {type(self).__name__}"
        )

    def verify_hmac(self, op: types.HMACOperation) -> bool | Awaitable[bool]:
        """Verify a digital signature that was created with a Hash-based
        Message Authentication Code (HMAC).
        """
        raise NotImplementedError(
            f"HMAC verification is not supported by {type(self).__name__}"
        )

    def verify_rsa(self, op: types.RSAOperation) -> bool | Awaitable[bool]:
        """Verify a digital signature that was created with a Hash-based
        Message Authentication Code (HMAC).
        """
        raise NotImplementedError(
            f"RSA verification is not supported by {type(self).__name__}"
        )

    @_verify.register
    def _verify_ec(
        self,
        op: types.EllipticCurveOperation
    ) -> bool | Awaitable[bool]:
        return self.verify_ec(op)

    @_verify.register
    def _verify_eddsa(
        self,
        op: types.EdDSAOperation
    ) -> bool | Awaitable[bool]:
        return self.verify_eddsa(op)

    @_verify.register
    def _verify_hmac(
        self,
        op: types.HMACOperation
    ) -> bool | Awaitable[bool]:
        return self.verify_hmac(op)

    @_verify.register
    def _verify_rsa(
        self,
        op: types.RSAOperation
    ) -> bool | Awaitable[bool]:
        return self.verify_rsa(op)