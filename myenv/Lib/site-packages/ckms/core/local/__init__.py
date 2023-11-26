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
"""Declares :class:`LocalProvider`."""
import functools
import hmac
import inspect
from typing import cast
from typing import Any

import aiofiles
from ckms.types import CipherText
from ckms.types import HMACOperation
from cryptography.exceptions import InvalidSignature
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import AEADCipherContext
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap

import ckms.types
from ckms import core
from ckms.core.provider import Provider
from ckms.lib import dsnparse
from ckms.utils import bytes_to_number
from ckms.utils import number_to_bytes
from .types import HMAC
from .types import Key
from .models import KeySpecification


class LocalProvider(Provider):
    """A :class:`~ckms.core.Provider` implementation that uses the
    local CPU to perform cryptographic operations.
    """
    require_algorithm: bool = True
    supported_rsa_algorithms: set[str] = {
        'RS256',
        'RS384',
        'RS512',
        'PS256',
        'PS384',
        'PS512',
        'RSA-OAEP',
        'RSA-OAEP-256',
        'RSA-OAEP-384',
        'RSA-OAEP-512',
    }
    supported_ed_curves: set[str] = {"Ed448", "X448", "Ed25519", "X25519"}
    spec: type[KeySpecification] = KeySpecification # type: ignore
   
    async def generate(
        self,
        op: ckms.types.GenerateKeyOperation
    ) -> Any: # type: ignore
        """Select the proper class and generate a new key."""
        result = self._generate(op.spec)
        if inspect.isawaitable(result):
            result = await result
        return result


    def parse_dsn(self, dsn: dsnparse.ParseResult) -> KeySpecification:
        return {
            **dsn.query_params, # type: ignore
            'provider': 'local',
            'key': {'path': dsn.path[1:]} # type: ignore
        }

    @functools.singledispatchmethod
    def _generate(self, spec: Any) -> Any:
        raise NotImplementedError(repr(spec))

    @_generate.register
    async def _generate_aes(self, spec: ckms.types.GenerateAES) -> Any:
        return algorithms.AES(await self.random(spec.length))

    @_generate.register
    def _generate_ec(self, spec: ckms.types.GenerateEllipticCurve) -> Any:
        generate, curve = self.inspector.get_ec_class(spec.curve)
        return generate(curve)

    @_generate.register
    async def _generate_hmac(self, spec: ckms.types.GenerateHMAC) -> Any:
        return HMAC(await self.random(spec.length))

    @_generate.register
    def _generate_rsa(self, spec: ckms.types.GenerateRSA) -> Any:
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=spec.length
        )

    @_generate.register
    def _generate_okp(self, spec: ckms.types.GenerateOKP) -> Any:
        cls = self.inspector.get_ed_class(spec.curve)
        return cls.generate()

    def get_digest_algorithm(self, algorithm: str) -> hashes.HashAlgorithm:
        """Return an instance of the selected `algorithm`."""
        assert algorithm in {'sha1', 'sha256', 'sha384', 'sha512'}, algorithm
        return getattr(hashes, str.upper(algorithm))()

    def get_key_identifier(self, spec: models.KeySpecification) -> str: # type: ignore
        """Generate a key identifier for the given private key."""
        return self.inspector.calculate_kid(spec.key) # type: ignore

    def get_padding(self, scheme: str, digest: str) -> padding.AsymmetricPadding:
        """Return an instance of the specified padding."""
        algorithm = self.get_digest_algorithm(digest)
        if scheme in {'EMSA-PSS', 'PSS'}:
            instance = padding.PSS(
                mgf=padding.MGF1(algorithm),
                salt_length=algorithm.digest_size
            )
        elif scheme in {'EMSA-PKCS1-v1_5', 'PKCS1v15'}:
            instance = padding.PKCS1v15()
        elif scheme in {'OAEP'}:
            instance = padding.OAEP(
                mgf=padding.MGF1(algorithm),
                algorithm=algorithm,
                label=None
            )
        else: # pragma: no cover
            raise ValueError(f"Unsupported scheme: {scheme}")
        return instance

    def get_public_key(self, spec: KeySpecification) -> Any | None:
        return spec.get_public_key()

    def unwrap_aes_wrap(self, op: ckms.types.AESKeywrapOperation) -> bytes:
        spec = op.get_keyspec()
        return aes_key_unwrap(
            wrapping_key=spec.get_private_bytes(),
            wrapped_key=bytes(op.content)
        )

    async def decrypt_aes(self, op: ckms.types.AESOperation) -> bytes:
        ct = op.get_ciphertext()
        if not op.get_initialization_vector():
            raise self.Undecryptable
        cipher = op.get_cipher()
        d = cipher.decryptor()
        if isinstance(d, AEADCipherContext) and ct.aad is not None:
            d.authenticate_additional_data(ct.aad)
        try:
            pt = d.update(await op.get_message()) + d.finalize()
        except InvalidTag:
            raise self.Undecryptable(
                detail=(
                    "Unable to decrypt the ciphertext using  Advanced "
                    "Encryption Standard (AES)."
                )
            )
        if op.padding:
            raise NotImplementedError
        return pt

    async def encrypt_aes(self, op: ckms.types.AESOperation) -> CipherText:
        iv = await self.random(12)
        cipher = op.get_cipher(iv=iv)
        e = cipher.encryptor()
        data = await op.get_message()
        if isinstance(e, AEADCipherContext) and op.aad is not None:
            e.authenticate_additional_data(op.aad)
        if op.padding:
            raise NotImplementedError
        buf = e.update(data) + e.finalize()
        return CipherText(
            aad=op.aad,
            buf=buf,
            iv=iv,
            tag=getattr(e, 'tag', None)
        )

    async def unwrap(self, op: ckms.types.KeywrapOperation) -> bytes:
        assert op.mode == 'aes'
        algorithm = op.get_private_key()
        return aes_key_unwrap(
            wrapping_key=algorithm.key,
            wrapped_key=await op.get_message()
        )

    async def decrypt_rsa(self, op: ckms.types.RSAOperation) -> bytes:
        key = op.get_private_key()
        return key.decrypt(
            ciphertext=await op.get_message(),
            padding=self.get_padding(op.padding, op.digest)
        )

    async def encrypt_rsa(self, op: ckms.types.RSAOperation) -> ckms.types.CipherText:
        key = op.get_public_key()
        return ckms.types.CipherText(
            buf=key.encrypt(
                await op.get_message(),
                padding=self.get_padding(op.padding, op.digest)
            )
        )

    async def fetch(self, blob: core.RemoteBlob) -> bytes:
        """Fetches the content of the remote blob using the parameters
        specified. Return a byte-string holding the content.
        """
        blob = Key.parse_obj(blob.dict()) # type: ignore
        async with aiofiles.open(blob.path, 'rb') as f: # type: ignore
            return await f.read() # type: ignore

    async def sign_ec(self, op: ckms.types.EllipticCurveOperation) -> bytes:
        key = cast(ec.EllipticCurvePrivateKey, op.spec.key)
        n = (key.curve.key_size + 7) // 8
        sig = key.sign(
            data=await op.get_digest(),
            signature_algorithm=ec.ECDSA(
                utils.Prehashed(self.get_digest_algorithm(op.digest))
            )
        )
        r, s = utils.decode_dss_signature(sig)
        return number_to_bytes(r, n) + number_to_bytes(s, n)

    async def sign_eddsa(self, op: ckms.types.EdDSAOperation) -> bytes:
        return op.spec.key.sign(await op.get_message())

    async def sign_hmac(self, op: ckms.types.HMACOperation) -> bytes:
        assert op.digestmod is not None
        mac = hmac.new(
            key=op.spec.key,
            digestmod=op.digestmod
        )
        async for chunk in op.chunks():
            mac.update(chunk)
        return mac.digest()

    async def sign_rsa(self, op: ckms.types.RSAOperation) -> bytes:
        return op.spec.key.sign(
            await op.get_digest(),
            padding=self.get_padding(op.padding, op.digest),
            algorithm=utils.Prehashed(self.get_digest_algorithm(op.digest))
        )

    async def verify_ec(self, op: ckms.types.EllipticCurveOperation) -> bool:
        if op.signature is None:
            raise TypeError("Signature can not be None.")
        public = op.get_public_key()
        n = (public.curve.key_size + 7) // 8
        try:
            public.verify(
                signature=utils.encode_dss_signature(
                    bytes_to_number(op.signature[:n]),
                    bytes_to_number(op.signature[n:]),
                ),
                data=await op.get_digest(),
                signature_algorithm=ec.ECDSA(
                    utils.Prehashed(self.get_digest_algorithm(op.digest))
                )
            )
            return True
        except InvalidSignature:
            return False

    async def verify_eddsa(self, op: ckms.types.EdDSAOperation) -> bool:
        key = op.spec.get_public_key()
        try:
            key.verify(op.signature, await op.get_message())
            return True
        except InvalidSignature:
            return False

    async def verify_hmac(self, op: HMACOperation) -> bool:
        assert op.digestmod is not None
        assert op.signature is not None
        mac = hmac.new(
            key=op.spec.key,
            digestmod=op.digestmod
        )
        async for chunk in op.chunks():
            mac.update(chunk)
        return hmac.compare_digest(op.signature, mac.digest())

    async def verify_rsa(self, op: ckms.types.RSAOperation) -> bool:
        public = op.get_public_key()
        try:
            public.verify(
                signature=op.signature,
                data=await op.get_digest(),
                padding=self.get_padding(op.padding, op.digest),
                algorithm=utils.Prehashed(self.get_digest_algorithm(op.digest))
            )
            return True
        except InvalidSignature:
            return False
