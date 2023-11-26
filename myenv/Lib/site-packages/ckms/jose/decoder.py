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
"""Declares :class:`Decoder`."""
import inspect
import functools
from typing import Any

from ckms.core.models import JOSEObject
from ckms.core.models.jsonwebsignature import JSONWebSignature
from ckms.core.models.jsonwebencryption_ import JSONWebEncryption
from ckms.utils import b64decode
from ckms.types import IKeychain
from ckms.types import JSONWebToken
from ckms.types import MalformedPayload
from .exceptions import InvalidSignature
from .joseheaderset import JOSEHeaderSet


class Decoder:
    """Providers an interface to decrypt and introspect JOSE objects."""
    __module__: str = 'ckms.jose'
    model: type[JOSEObject] = JOSEObject
    decrypter: IKeychain
    verifier: IKeychain
    jwt_types: set[str]

    @staticmethod
    def introspect(
        value: str | bytes,
        model: type[JSONWebToken] = JSONWebToken,
        accept: set[str] = {"at+jwt", "secevent+jwt", "jwt"}
    ) -> tuple[JOSEHeaderSet, JSONWebToken | None]:
        """Introspect a JOSE object and return the list of :class:`JOSEHeader`
        instances for all recipients or signatures.
        """
        obj = JOSEObject.parse(value)
        claims = None
        if isinstance(obj, JSONWebSignature) and obj.is_jwt(accept=accept):
            claims = obj.get_claims(model)
        return (JOSEHeaderSet(headers=obj.get_headers()), claims)

    def __init__(
        self,
        decrypter: IKeychain,
        verifier: IKeychain,
        jwt_types: set[str] | None = None
    ):
        self.decrypter = decrypter
        self.jwt_types = jwt_types or {"at+jwt", "jwt", "secevent+jwt"}
        self.verifier = verifier

    async def decode(
        self,
        serialized: bytes | str,
        verify: bool = True,
        require_kid: bool = True,
        accept: set[str] = {"at+jwt", "jwt", "jwt+secevent"},
        **kwargs: Any
    ):
        """Decode the given JOSE object `obj`, which is either JSON Web
        Encryption (JWE) or a JSON Web Signature (JWS) using any supported
        serialization format.

        The `verify` parameter indicates if the signatures must validate
        using the configured :class:`ckms.types.IKeychain` instance. By
        default, all signatures must validate with a key that was
        preregistered in the keychain.

        The :meth:`decode()` method requires all signers to provide a
        ``kid`` header parameter used to lookup the corresponding (public)
        key from the keychain. This behavior may be changed by providing
        the `require_kid` parameter. If `require_kid` is ``False``, then
        :class:`Decoder` attempts all keys in :attr:`Decoder.keychain`
        that match the signature algorithm. The default value is ``True``.
        """
        obj = await self._decode(self.model.parse(serialized))
        if isinstance(obj, JSONWebSignature):
            if verify\
            and not await obj.verify(self.verifier, require_kid=require_kid):
                raise InvalidSignature
            typ = obj.get_type()
            payload = obj.get_payload()

            # TODO: Implement a parser system like in cbra
            if accept:
                payload = obj.claims(accept=accept)
            elif typ is not None and typ in self.jwt_types:
                payload = JSONWebToken.frompayload(payload)
            else:
                payload = b64decode(payload)
        elif isinstance(obj, JSONWebToken):
            payload = obj
        else:
            payload = obj
        return payload

    async def jws(self, token: bytes | str) -> JSONWebSignature:
        """Like :meth:`decode()`, but returns the unverified and unparsed
        JSON Web Signature (JWS). If `token` is not a JWS, raise an
        exception.
        """
        obj = await self._decode(self.model.parse(token))
        if not isinstance(obj, JSONWebSignature):
            raise MalformedPayload(
                detail=(
                    "The applications expects a JSON Web Signature (JWS)."
                )
            )
        return obj

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
        if isinstance(accept, str):
            accept = {accept}
        sig = await self.jws(token)
        return sig, sig.claims(accept or self.jwt_types)

    @functools.singledispatchmethod
    def _decode(self, obj: Any) -> Any:
        raise NotImplementedError(repr(obj))

    @_decode.register
    async def _decode_jwe(self, obj: JSONWebEncryption) -> bytes | JSONWebToken | JSONWebSignature:
        cty = obj.get_content_type()
        typ = obj.get_type()
        payload = obj.decrypt(self.decrypter)
        if inspect.isawaitable(payload):
            payload = await payload
        if cty is None and typ in self.jwt_types:
            # JWE with no further content type specification. If this is JWT,
            # then the JWE contains an unsigned JSON Web Token (JWT). Otherwise,
            # we can not determine the payload content type and thus return the
            # raw byte-sequence.
            payload = JSONWebToken.fromjson(payload)
        elif cty in {"jose", "jose+json", *self.jwt_types}:
            # Nested JWT -> In the case that nested signing or
            # encryption is employed, this Header Parameter MUST
            # be present (RFC 7519, 5.2).
            payload = JOSEObject.parse(payload)
            assert isinstance(payload, JSONWebSignature)
        return payload

    @_decode.register
    async def _decode_jws(self, obj: JSONWebSignature) -> JSONWebSignature:
        return obj