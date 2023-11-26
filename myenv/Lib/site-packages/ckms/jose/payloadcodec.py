"""Declares :class:`PayloadCodec`."""
import typing
from typing import Any

from ckms.core import Keychain
from ckms.core.models import JSONWebSignature
from ckms.types import ClaimSet
from ckms.types import Data
from ckms.types import Encrypter
from ckms.types import IKeychain
from ckms.types import IKeySpecification
from ckms.types import JSONWebToken
from ckms.types import JSONWebKeySet
from ckms.types import MalformedObject
from ckms.types import Signer
from .decoder import Decoder
from .encoder import Encoder
from .joseheaderset import JOSEHeaderSet
from .josepayload import JOSEPayload
from .jsonwebkeysetresolver import JSONWebKeySetResolver
from .nullissuercache import NullIssuerCache
from .nulltokenconsumer import NullTokenConsumer
from .types import BaseIssuerCache
from .types import BaseTokenConsumer
from .validator import Validator


SUPPORTED_ALGORITHMS = [
    "RSA1_5",
    "RSA-OAEP",
    "RSA-OAEP-256",
    "RSA-OAEP-384",
    "RSA-OAEP-512",
    "A128KW",
    "A192KW",
    "A256KW",
    "A128GCMKW",
    "A192GCMKW",
    "A256GCMKW",
    "dir",
    "ECDH-ES",
    "ECDH-ES+A128KW",
    "ECDH-ES+A192KW",
    "ECDH-ES+A256KW",
    "PBES2-HS256+A128KW",
    "PBES2-HS256+A192KW",
    "PBES2-HS256+A256KW",
]


class PayloadCodec:
    """Exposes an interface to decode and encode a JSON Web Token (JWT),
    JSON Web Encryption (JWE) or JSON Web Signature (JWS).
    """
    __module__: str = 'ckms.jose'
    allow_compact: bool
    allow_flattened: bool
    decoder: Decoder
    encoder: Encoder
    encryption_keys: list[str]
    signer: IKeychain
    verifier: IKeychain
    decrypter: IKeychain
    encrypter: IKeychain
    allow_jwks_import: bool
    signing_keys: list [str | IKeySpecification]
    trusted_issuers: set[str]
    validator: Validator | None

    @staticmethod
    def introspect(
        token: str | bytes,
        model: type[JSONWebToken] = JSONWebToken,
        accept: set[str] = {"at+jwt", "jwt"}
    ) -> tuple[JOSEHeaderSet, JSONWebToken | None]:
        """Introspect the token. Return a :class:`ckms.jose.JOSEHeaderSet`
        instance, and a :class:`ckms.types.JSONWebToken` instance representing the
        claims if the token is a JSON Web Token (JWT), otherwise the second
        variable in the tuple is byte-sequence enclosed in the object.
        """
        return Decoder.introspect(token, model=model, accept=accept)

    @classmethod
    def fromjwks(cls, jwks: JSONWebKeySet) -> 'PayloadCodec':
        return cls(
            encryption_keys=jwks.as_list(), # type: ignore
            verifier=jwks
        )

    @classmethod
    async def verify(
        cls,
        *,
        token: str,
        resolver: JSONWebKeySetResolver,
        accept: set[str] = {"jwt", "at+jwt", "secevent+jws"},
        cache: BaseIssuerCache = NullIssuerCache(),
        consumer: BaseTokenConsumer = NullTokenConsumer()
    ) -> bytes | str | JSONWebToken:
        """Verify the signature of a JSON Web Token (KWT)."""
        _, jwt = cls.introspect(token, accept=accept)
        if jwt is None or jwt.iss is None:
            raise MalformedObject
        jwks = await cache.get(jwt.iss)
        if jwks is None:
            jwks = await resolver.resolve(jwt)
            await cache.add(jwt.iss, jwks)
        codec = cls(verifier=jwks)
        jwt = await codec.decode(token, accept=accept)
        assert isinstance(jwt, JSONWebToken) # nosec
        return await consumer.consume(jwt)

    def __init__(
        self,
        signer: IKeychain | None = None,
        verifier: IKeychain | None = None,
        decrypter: IKeychain | None = None,
        encrypter: IKeychain | None = None,
        required_claims: typing.Optional[typing.Set[str]] = None,
        jwks_import: bool = False,
        audiences: typing.Optional[typing.Set[str]] = None,
        trusted_issuers: typing.Optional[typing.Set[str]] = None,
        content_encryption: str = "A256GCM",
        signing_keys: list[str | IKeySpecification] | None = None,
        encryption_keys: list[str] | list[IKeySpecification | JSONWebKeySet] | None = None,
        allow_compact: bool = True,
        allow_flattened: bool = True
    ):
        """A :class:`PayloadCodec` instance governs the rules under which
        objects are deserialized, decoded and instantiated into the
        corresponding Python objects.

        The `verifier` and `decrypter` parameters are required and specify
        which :class:`~ckms.types.IKeychain` implementations are used to verify
        digital signatures and decrypt JWE payloads. A common configuration is
        to provide a :class:`~ckms.types.JSONWebKeySet` holding public keys
        exclusively as the `verifier` parameter, and a :class:`ckms.core.Keychain`
        or similar as the `decrypter` parameter. If any of these parameters
        is omitted, then the respective operations can not be performed by
        :class:`PayloadCodec` and will if the (public) keys can not be
        resolved otherwise (e.g. through the issuer JWKS URI for example).

        A provider of entropy may be specified using the `random` argument.

        The `required_claims` specifies the claims the must be present when
        the payload is a JWT. If any of these claims is missing, then
        validation of the JWT fails. Null values are not considered missing
        claims.

        The `jwks_import` parameter is a boolean indicating if a JSON
        Web Key Set (JWKS) or JSON Web Key (JWK) may be imported using either
        the ``iss`` (using OAuth 2.0 metadata discovery) or ``jku`` claims,
        respectively. The default is ``False``.

        With the `trusted_issuers` parameter the set of issuers that are
        trusted by the codec may be specified. Any token that has an ``iss``
        claim that is not in this set, is rejected. If `jwks_import``
        is ``True``, then a JWK(S) may be imported if the issuer is in
        this set.  If `trusted_issuers` is ``None`` or an empty set, then the
        `iss` claim is not considered during JWT validation.

        Similarly, the `audiences` parameter specifies the set of audiences
        with which the set of audiences in the `aud` claim of a JWT must
        intersect. If `audiences` is ``None`` or an empty set, then the
        `aud` claim is not considered during JWT validation.

        Default signers may be configured with the `signing_keys` parameter,
        which is a list of strings specifying the keys to sign a JWS with.
        The signatures are created in order. Likewise, the `encryption_keys`
        parameter is used to specify default encryption keys.
        """
        self.signer = signer if signer is not None else Keychain()
        self.verifier = verifier if verifier is not None else Keychain()
        self.decrypter = decrypter if decrypter is not None else Keychain()
        self.encrypter = encrypter if encrypter is not None else Keychain()
        self.decoder = Decoder(decrypter=self.decrypter, verifier=self.verifier)
        self.encoder = Encoder(
            allow_compact=allow_compact,
            allow_flattened=allow_flattened,
            encrypter=self.encrypter,
            encryption_keys=encryption_keys,
            signer=self.signer,
            signing_keys=signing_keys
        )
        self.jwks_import = jwks_import
        self.signing_keys = signing_keys or []
        self.trusted_issuers = set(trusted_issuers or [])
        self.issuers = {}
        self.validator = None
        self.content_encryption = content_encryption

    async def decode(
        self,
        token: bytes | str,
        verify: bool = True,
        accept: set[str] = {"at+jwt", "jwt", "secevent+jwt"},
        require_kid: bool = True,
        _type: type = JSONWebToken
    ) -> bytes | str | JSONWebToken:
        """Decode `token` and return the payload, which is either a
        :class:`~ckms.types.JSONWebToken` or byte-sequence. See also
        :meth:`~ckms.jose.Decoder.decode()`.
        """
        return await self.decoder.decode(
            token,
            verify=verify,
            accept=accept,
            require_kid=require_kid
        )

    async def jws(self, token: bytes | str) -> JSONWebSignature:
        """Like :meth:`decode()`, but returns the unverified and unparsed
        JSON Web Signature (JWS). If `token` is not a JWS, raise an
        exception.
        """
        return await self.decoder.jws(token)

    async def jwt(
        self,
        token: bytes | str,
        accept: set[str] | str | None = None
    ) -> tuple[JSONWebSignature, JSONWebToken]:
        """Like :meth:`decode()`, but returns a tuple containing the
        unverified JSON Web Signature (JWS) and its claims set. If
        `token` is not a JWS, or does not have a claims set, raise
        an exception.
        """
        return await self.decoder.jwt(token, accept=accept)

    def encode(
        self,
        payload: bytes | dict[str, Any] | str | ClaimSet | Data,
        sign: bool = True,
        encrypt: bool = True,
        content_type: str | None = None,
        claimset_class: type[ClaimSet] = ClaimSet,
        signing_keys: list[str] | None = None,
        signers: list[str] | list[Signer] | None = None,
        encrypters: list[str] | list[Encrypter] | None = None,
        allow_compact: bool = True,
        allow_flattened: bool = True
    ) -> JOSEPayload:
        return self.encoder.encode(
            content=payload,
            sign=sign,
            encrypt=encrypt,
            content_type=content_type,
            claimset_class=claimset_class,
            signing_keys=signing_keys,
            signers=signers,
            encrypters=encrypters,
            allow_compact=True,
            allow_flattened=True
        )

    def get_key_algorithm(self, using: str) -> str | None:
        """Return the algorithm for the specified key `using`."""
        return self.signer.get(using).algorithm
