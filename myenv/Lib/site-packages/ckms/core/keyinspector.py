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
"""Declares :class:`KeyInspector`."""
import functools
import hashlib
import typing

from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

from ckms import types
from ckms.types import IKeyInspector
from ckms.types import KeyOperationType
from ckms.utils import b64encode_int
from ckms.utils import b64encode
from ckms.utils import b64decode_int
from ckms.utils import b64decode


JWKReturnType = dict[str, str | list[str]]
KeyType: typing.TypeAlias = IKeyInspector.KeyType


class KeyInspector(types.IKeyInspector):
    """Inspects keys from the :mod:`cryptography` package."""
    __module__: str = 'ckms.core'

    CurveType: typing.TypeAlias = typing.Union[
        ec.SECP256R1,
        ec.SECP384R1,
        ec.SECP521R1,
        ec.SECP256K1
    ]

    #: Maintains a mapping between curve names.
    curve_mapping: dict[typing.Any, typing.Any] = {
        "P-256": ec.SECP256R1,
        "P-384": ec.SECP384R1,
        "P-521": ec.SECP521R1,
        "P-256K": ec.SECP256K1,
        types.EllipticCurveType.P256: ec.SECP256R1,
        types.EllipticCurveType.P384: ec.SECP384R1,
        types.EllipticCurveType.P521: ec.SECP521R1,
        types.EllipticCurveType.P256K: ec.SECP256K1,
        ec.SECP256R1.name: "P-256",
        ec.SECP384R1.name: "P-384",
        ec.SECP521R1.name: "P-521",
        ec.SECP256K1.name: "P-256K"
    }

    #: Maps types to curves.
    ed_curve_map: dict[typing.Any, typing.Any] = {
        ed448.Ed448PublicKey: "Ed448",
    }
    ed_curve_map.update({y: x for x, y in ed_curve_map.items()})

    #: Map algorithms to curves
    algorithm_curves: dict[str, str] = {
        'ES256': 'P-256',
        'ES384': 'P-384',
        'ES512': 'P-521',
        'ES256K': 'P-256K',
    }

    #: Map algorithms to digest algorithms
    algorithm_digests: dict[str, str] = {
        'ES256'         : 'sha256',
        'ES384'         : 'sha384',
        'ES512'         : 'sha512',
        'ES256K'        : 'sha256',
        'HS256'         : 'sha256',
        'HS384'         : 'sha384',
        'HS512'         : 'sha512',
        'PS256'         : 'sha256',
        'PS384'         : 'sha384',
        'PS512'         : 'sha512',
        'RS256'         : 'sha256',
        'RS384'         : 'sha384',
        'RS512'         : 'sha512',
    }

    #: Maps algorithms to uses
    algorithm_use: dict[str, str] = {
        'EdDSA'         : 'sig',
        'ES256'         : 'sig',
        'ES384'         : 'sig',
        'ES512'         : 'sig',
        'ES256K'        : 'sig',
        'HS256'         : 'sig',
        'HS384'         : 'sig',
        'HS512'         : 'sig',
        'PS256'         : 'sig',
        'PS384'         : 'sig',
        'PS512'         : 'sig',
        'RS256'         : 'sig',
        'RS384'         : 'sig',
        'RS512'         : 'sig',
        'ECDH-ES'       : 'enc',
        'ECDH-ES+A128KW': 'enc',
        'ECDH-ES+A192KW': 'enc',
        'ECDH-ES+A256KW': 'enc',
        'RSA1_5'        : 'enc',
        'RSA-OAEP'      : 'enc',
        'RSA-OAEP-256'  : 'enc',
        'RSA-OAEP-384'  : 'enc',
        'RSA-OAEP-512'  : 'enc',
        'A128KW'        : 'enc',
        'A192KW'        : 'enc',
        'A256KW'        : 'enc',
        'A128GCM'       : 'enc',
        'A192GCM'       : 'enc',
        'A256GCM'       : 'enc',
        'A128GCMKW'     : 'enc',
        'A192GCMKW'     : 'enc',
        'A256GCMKW'     : 'enc',
    }

    @staticmethod
    def get_ed_curve(
        key: (
            ed448.Ed448PublicKey
            | ed25519.Ed25519PublicKey
            | x448.X448PublicKey
            | x25519.X25519PublicKey
        )
    ) -> str:
        """Return the name of the curve."""
        if isinstance(key, (ed448.Ed448PrivateKey, ed448.Ed448PublicKey)):
            return "Ed448"
        elif isinstance(key, (x448.X448PrivateKey, x448.X448PublicKey)):
            return "X448"
        elif isinstance(key, (ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey)):
            return "Ed25519"
        elif isinstance(key, (x25519.X25519PrivateKey, x25519.X25519PublicKey)): #type: ignore
            return "X25519"
        else:
            raise NotImplementedError

    @functools.singledispatchmethod
    def calculate_kid(
        self,
        key: KeyType | algorithms.AES | str
    ) -> str:
        """Calculate a key identifier for the given `key`.
        
        If `key` is a string, it is assumed to be the resource address
        of a cloud KMS resource, otherwise `key` must be a key type from
        the :mod:`cryptography` package.
        """
        raise NotImplementedError(key)

    @calculate_kid.register
    def _calculate_kid_ec_public(self, key: ec.EllipticCurvePublicKey) -> str:
        h = hashlib.sha3_256() # nosec
        l = (key.curve.key_size + 7) // 8
        n = key.public_numbers()
        h.update(str.encode(self.curve_mapping[key.curve.name]))
        h.update(str.encode('EC'))
        h.update(int.to_bytes(n.x, l, 'big'))
        h.update(int.to_bytes(n.y, l, 'big'))
        return self.encode_kid(h.digest())

    @calculate_kid.register
    def _calculate_kid_ec_private(self, key: ec.EllipticCurvePrivateKey) -> str:
        return self._calculate_kid_ec_public(key.public_key())

    @calculate_kid.register
    def _calculate_kid_ed448_public(self, key: ed448.Ed448PublicKey) -> str:
        return self._calculate_kid_ed(key)

    @calculate_kid.register
    def _calculate_kid_ed448_private(self, key: ed448.Ed448PrivateKey) -> str:
        return self._calculate_kid_ed(key.public_key())

    @calculate_kid.register
    def _calculate_kid_ed25519_public(self, key: ed25519.Ed25519PublicKey) -> str:
        return self._calculate_kid_ed(key)

    @calculate_kid.register
    def _calculate_kid_ed25519_private(self, key: ed25519.Ed25519PrivateKey) -> str:
        return self._calculate_kid_ed(key.public_key())

    @calculate_kid.register
    def _calculate_kid_x448_public(self, key: x448.X448PublicKey) -> str:
        return self._calculate_kid_ed(key)

    @calculate_kid.register
    def _calculate_kid_x448_private(self, key: x448.X448PrivateKey) -> str:
        return self._calculate_kid_ed(key.public_key())

    @calculate_kid.register
    def _calculate_kid_x25519_public(self, key: x25519.X25519PublicKey) -> str:
        return self._calculate_kid_ed(key)

    @calculate_kid.register
    def _calculate_kid_x25519_private(self, key: x25519.X25519PrivateKey) -> str:
        return self._calculate_kid_ed(key.public_key())

    def _calculate_kid_ed(
        self,
        key: (
            ed448.Ed448PublicKey
            | ed25519.Ed25519PublicKey
            | x448.X448PublicKey
            | x25519.X25519PublicKey
        )
    ) -> str:
        h = hashlib.sha3_256()
        h.update(str.encode(self.get_ed_curve(key)))
        h.update(str.encode("OKP"))
        h.update(
            key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        )
        return self.encode_kid(h.digest())

    @calculate_kid.register
    def _calculate_kid_rsa_public(self, key: rsa.RSAPublicKey) -> str:
        h = hashlib.sha3_256()
        l = key.key_size // 8
        n = key.public_numbers()
        h.update(int.to_bytes(n.e, 3, 'big'))
        h.update(str.encode("RSA"))
        h.update(int.to_bytes(n.n, l, 'big'))
        return self.encode_kid(h.digest())

    @calculate_kid.register
    def _calculate_kid_rsa_private(self, key: rsa.RSAPrivateKey) -> str:
        return self._calculate_kid_rsa_public(key.public_key())

    @calculate_kid.register
    def _calculate_kid_aes(self, algorithm: algorithms.AES) -> str:
        return self._calculate_kid_bytes(algorithm.key)

    @calculate_kid.register
    def _calculate_kid_str(self, key: str) -> str:
        h = hashlib.sha3_256() # nosec
        h.update(str.encode(key, 'ascii'))
        h.update(b'kty')
        return self.encode_kid(h.digest())

    @calculate_kid.register
    def _calculate_kid_bytes(self, value: bytes) -> str:
        # Generic method to calculate a key identifier based
        # on an opaque external identifier, such as the address
        # of a cloud KMS resource.
        h = hashlib.sha3_256(value)
        h.update(str.encode("oct"))
        return self.encode_kid(h.digest())

    def to_bytes(self, key: typing.Any) -> bytes:
        # TODO: Not all keys use the PEM format.
        return self.to_pem(key)

    @functools.singledispatchmethod
    def to_pem(self, key: KeyType) -> bytes:
        # TODO: HMAC/AES are not in the PEM format.
        if isinstance(key, bytes):
            return key
        elif isinstance(key, algorithms.AES):
            return key.key
        else:
            raise NotImplementedError(type(key))

    @to_pem.register
    def _ed448_public_to_pem(self, key: ed448.Ed448PublicKey) -> bytes:
        return self._ed_public_to_pem(key)

    @to_pem.register
    def _ed448_private_to_pem(self, key: ed448.Ed448PrivateKey) -> bytes:
        return self._ed_private_to_pem(key)

    @to_pem.register
    def _x448_public_to_pem(self, key: x448.X448PublicKey) -> bytes:
        return self._ed_public_to_pem(key)

    @to_pem.register
    def _x448_private_to_pem(self, key: x448.X448PrivateKey) -> bytes:
        return self._ed_private_to_pem(key)

    @to_pem.register
    def _ed25519_public_to_pem(self, key: ed25519.Ed25519PublicKey) -> bytes:
        return self._ed_public_to_pem(key)

    @to_pem.register
    def _ed25519_private_to_pem(self, key: ed25519.Ed25519PrivateKey) -> bytes:
        return self._ed_private_to_pem(key)

    @to_pem.register
    def _x25519_public_to_pem(self, key: x25519.X25519PublicKey) -> bytes:
        return self._ed_public_to_pem(key)

    @to_pem.register
    def _x25519_private_to_pem(self, key: x25519.X25519PrivateKey) -> bytes:
        return self._ed_private_to_pem(key)

    def _ed_public_to_pem(
        self,
        key: (
            ed448.Ed448PublicKey
            | ed25519.Ed25519PublicKey
            | x448.X448PublicKey
            | x25519.X25519PublicKey
        )
    ) -> bytes:
        return key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

    def _ed_private_to_pem(
        self,
        key: (
            ed448.Ed448PrivateKey
            | ed25519.Ed25519PrivateKey
            | x448.X448PrivateKey
            | x25519.X25519PrivateKey
        )
    ) -> bytes:
        return key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )

    @to_pem.register
    def _ec_public_to_pem(self, key: ec.EllipticCurvePublicKey) -> bytes:
        return self._pkcs_public_to_pem(key)

    @to_pem.register
    def _ec_private_to_pem(self, key: ec.EllipticCurvePrivateKey) -> bytes:
        return self._pkcs_private_to_pem(key)

    @to_pem.register
    def _rsa_public_to_pem(self, key: rsa.RSAPublicKey) -> bytes:
        return self._pkcs_public_to_pem(key)

    @to_pem.register
    def _rsa_private_to_pem(self, key: rsa.RSAPrivateKey) -> bytes:
        return self._pkcs_private_to_pem(key)

    def _pkcs_public_to_pem(self, key: rsa.RSAPublicKey|ec.EllipticCurvePublicKey):
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def _pkcs_private_to_pem(self, key: rsa.RSAPrivateKey|ec.EllipticCurvePrivateKey):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def get_algorithm_use(self, algorithm: str) -> str:
        """Return the `use` parameter based on a given algorithm."""
        return self.algorithm_use[algorithm]

    @functools.singledispatchmethod
    def to_jwk(
        self,
        key: KeyType | algorithms.AES | bytes
    ) -> JWKReturnType:
        """Return a dictionary holding a representation of the key as
        a JSON Web Key (JWK).
        """
        raise NotImplementedError

    @to_jwk.register
    def _aes_to_jwk(self, algorithm: algorithms.AES) -> JWKReturnType:
        return self._jwk_properties(
            key=algorithm,
            kty="oct",
            k=bytes.decode(b64encode(algorithm.key), 'ascii')
        )

    @to_jwk.register
    def _bytes_to_jwk(self, key: bytes) -> JWKReturnType:
        return self._jwk_properties(
            key=key,
            kty="oct",
            k=bytes.decode(b64encode(key), 'ascii')
        )

    @to_jwk.register
    def _ec_public_to_jwk(self, key: ec.EllipticCurvePublicKey) -> JWKReturnType:
        numbers = key.public_numbers()
        return self._jwk_properties(
            key=key,
            kty="EC",
            crv=self.curve_mapping[key.curve.name],
            x=b64encode_int(numbers.x),
            y=b64encode_int(numbers.y)
        )

    @to_jwk.register
    def _ec_private_to_jwk(self, key: ec.EllipticCurvePrivateKey) -> JWKReturnType:
        numbers = key.private_numbers()
        return self._jwk_properties(
            key=key,
            kty="EC",
            crv=self.curve_mapping[key.curve.name],
            x=b64encode_int(numbers.public_numbers.x),
            y=b64encode_int(numbers.public_numbers.y),
            d=b64encode_int(numbers.private_value)
        )

    @to_jwk.register
    def _ed448_public_to_jwk(self, key: ed448.Ed448PublicKey) -> JWKReturnType:
        return self._jwk_properties(
            key=key,
            kty="OKP",
            alg='EdDSA',
            use='sig',
            crv="Ed448",
            x=b64encode(
                key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )
        )

    @to_jwk.register
    def _ed448_private_to_jwk(self, key: ed448.Ed448PrivateKey) -> JWKReturnType:
        public = key.public_key()
        return self._jwk_properties(
            key=key,
            kty="OKP",
            alg='EdDSA',
            use='sig',
            crv="Ed448",
            x=b64encode(
                public.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            ),
            d=b64encode(
                key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        )

    @to_jwk.register
    def _x448_public_to_jwk(self, key: x448.X448PublicKey) -> JWKReturnType:
        return self._jwk_properties(
            key=key,
            kty="OKP",
            use='enc',
            crv="X448",
            x=b64encode(
                key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )
        )

    @to_jwk.register
    def _x448_private_to_jwk(self, key: x448.X448PrivateKey) -> JWKReturnType:
        public = key.public_key()
        return self._jwk_properties(
            key=key,
            kty="OKP",
            use='enc',
            crv="X448",
            x=b64encode(
                public.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            ),
            d=b64encode(
                key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        )

    @to_jwk.register
    def _ed25519_public_to_jwk(self, key: ed25519.Ed25519PublicKey) -> JWKReturnType:
        return self._jwk_properties(
            key=key,
            kty="OKP",
            alg='EdDSA',
            use='sig',
            crv="Ed25519",
            x=b64encode(
                key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )
        )

    @to_jwk.register
    def _ed25519_private_to_jwk(self, key: ed25519.Ed25519PrivateKey) -> JWKReturnType:
        public = key.public_key()
        return self._jwk_properties(
            key=key,
            kty="OKP",
            alg='EdDSA',
            use='sig',
            crv="Ed25519",
            x=b64encode(
                public.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            ),
            d=b64encode(
                key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        )

    @to_jwk.register
    def _x25519_public_to_jwk(self, key: x25519.X25519PublicKey) -> JWKReturnType:
        return self._jwk_properties(
            key=key,
            kty="OKP",
            use="enc",
            crv="X25519",
            x=b64encode(
                key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )
        )

    @to_jwk.register
    def _x25519_private_to_jwk(self, key: x25519.X25519PrivateKey) -> JWKReturnType:
        public = key.public_key()
        return self._jwk_properties(
            key=key,
            kty="OKP",
            use="enc",
            crv="X25519",
            x=b64encode(
                public.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            ),
            d=b64encode(
                key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        )

    @to_jwk.register
    def _rsa_public_to_jwk(self, key: rsa.RSAPublicKey) -> JWKReturnType:
        numbers = key.public_numbers()
        return self._jwk_properties(
            key=key,
            kty="RSA",
            n=b64encode_int(numbers.n),
            e=b64encode_int(numbers.e)
        )

    @to_jwk.register
    def _rsa_private_to_jwk(self, key: rsa.RSAPrivateKey) -> JWKReturnType:
        numbers = key.private_numbers()
        return self._jwk_properties(
            key=key,
            kty="RSA",
            n=b64encode_int(numbers.public_numbers.n),
            e=b64encode_int(numbers.public_numbers.e),
            d=b64encode_int(numbers.d),
            p=b64encode_int(numbers.p),
            q=b64encode_int(numbers.q),
            dp=b64encode_int(numbers.dmp1),
            dq=b64encode_int(numbers.dmq1),
            qi=b64encode_int(numbers.iqmp),
        )

    def _jwk_properties(
        self,
        key: KeyType | algorithms.AES | bytes,
        **claims: typing.Any
    ) -> JWKReturnType:
        return {
            **claims,
            'kid': self.calculate_kid(key)
        }

    def from_jwk(
        self,
        jwk: dict[str, str]
    ) -> KeyType | bytes: # pragma: no cover
        """Create a new key instance from a dictionary holding a JSON
        Web Key (JWK).
        """
        kty = jwk.get('kty')
        crv = jwk.get('crv')
        claims = set(jwk.keys())
        rsa_claims = {'d', 'p', 'q', 'dp', 'dq', 'qi'}
        if kty is None:
            raise ValueError("The 'kty' claim needs to be defined.")
        if kty not in {"oct", "EC", "OKP", "RSA"}:
            raise ValueError(f"Unknown key type: '{kty}'")
        if (kty == "EC" and crv not in self.curve_mapping)\
        or kty == "OKP" and crv not in {"Ed448", "X448", "Ed25519", "X25519"}:
            raise ValueError("The 'crv' claim must contain a known curve.")
        if kty == "oct":
            if 'k' not in claims:
                raise ValueError("Octet keys need the 'k' claim.")
        elif kty == "EC":
            if not claims > {'x', 'y'}:
                raise ValueError(
                    "Elliptic curve keys need the 'x', 'y' "
                    "and optionally 'd' claims."
                )
        elif kty == "OKP":
            if 'x' not in claims:
                raise ValueError(
                    "EdDSA keys need the 'x' and optionally the 'd' "
                    "claims."
                )
        elif kty == "RSA":
            if not claims >= {'e', 'n'}:
                raise ValueError(
                    "RSA keys need at least the 'e' and 'n' "
                    "parameters."
                )
            if (rsa_claims & claims) and not claims > rsa_claims:
                raise ValueError("Missing claims for RSA private key.")

        key = None
        if kty == "oct":
            key = b64decode(jwk['k'])
        elif kty == "EC":
            numbers = ec.EllipticCurvePublicNumbers(
                curve=self.curve_mapping[crv](),
                x=b64decode_int(jwk['x']),
                y=b64decode_int(jwk['y']),
            )
            key = numbers.public_key()
            if 'd' in jwk:
                numbers = ec.EllipticCurvePrivateNumbers(
                    private_value=b64decode_int(jwk['d']),
                    public_numbers=numbers
                )
                key = numbers.private_key()

        elif kty == "OKP":
            public_factory = private_factory = None
            if crv == "Ed448":
                public_factory, private_factory = (
                    ed448.Ed448PublicKey.from_public_bytes,
                    ed448.Ed448PrivateKey.from_private_bytes
                )
            elif crv == "X448":
                public_factory, private_factory = (
                    x448.X448PublicKey.from_public_bytes,
                    x448.X448PrivateKey.from_private_bytes
                )
            elif crv == "Ed25519":
                public_factory, private_factory = (
                    ed25519.Ed25519PublicKey.from_public_bytes,
                    ed25519.Ed25519PrivateKey.from_private_bytes
                )
            elif crv == "X25519":
                public_factory, private_factory = (
                    x25519.X25519PublicKey.from_public_bytes,
                    x25519.X25519PrivateKey.from_private_bytes
                )
            assert public_factory is not None # nosec
            assert private_factory is not None # nosec
            key = public_factory(b64decode(jwk['x']))
            if 'd' in claims:
                key = private_factory(b64decode(jwk['d']))

        elif kty == "RSA":
            numbers = rsa.RSAPublicNumbers(
                e=b64decode_int(jwk['e']),
                n=b64decode_int(jwk['n']),
            )
            key = numbers.public_key()
            if rsa_claims & claims:
                numbers = rsa.RSAPrivateNumbers(
                    public_numbers=numbers,
                    d=b64decode_int(jwk['d']),
                    p=b64decode_int(jwk['p']),
                    q=b64decode_int(jwk['q']),
                    dmp1=b64decode_int(jwk['dp']),
                    dmq1=b64decode_int(jwk['dq']),
                    iqmp=b64decode_int(jwk['qi'])
                )
                key = numbers.private_key()
        else:
            raise ValueError("Unable to parse the JWK.")
        assert key is not None # nosec
        return key

    def encode_kid(self, digest: bytes) -> str:
        return bytes.decode(b64encode(digest), 'ascii') # nosec

    def get_algorithm_curve(self, algorithm: str) -> str | None:
        return self.algorithm_curves.get(algorithm)

    def get_ec_class(
        self,
        curve: types.EllipticCurveType | str
    ) -> tuple[typing.Callable[..., ec.EllipticCurvePrivateKey], ec.EllipticCurve]:
        return ec.generate_private_key, self.curve_mapping[curve]

    def get_ed_class(
        self,
        curve: str
    ) -> ed448.Ed448PrivateKey | ed25519.Ed25519PrivateKey | x448.X448PrivateKey | x25519.X25519PrivateKey:
        if curve not in {'Ed448', 'Ed25519', 'X448', 'X25519'}: # pragma: no cover
            # Should not happen, but check anyway as a failsafe against RCE
            raise ValueError("Unsupported curve.")
        return getattr(globals()[str.lower(curve)], f'{curve}PrivateKey')

    def get_hashing_algorithm(self, algorithm: str) -> str | None:
        """Return a string indicating the hashing algorithm."""
        return self.algorithm_digests.get(algorithm)

    def get_public_key_ops(self, private: list[KeyOperationType]) -> list[KeyOperationType]:
        public: list[KeyOperationType] = []
        if KeyOperationType.decrypt in private:
            public.append(KeyOperationType.encrypt)
        if KeyOperationType.deriveKey in private:
            public.append(KeyOperationType.deriveKey)
        if KeyOperationType.sign in private:
            public.append(KeyOperationType.verify)
        if KeyOperationType.unwrapKey in private:
            public.append(KeyOperationType.wrapKey)
        return public