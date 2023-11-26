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
"""Declares :class:`JSONWebSignature`."""
import json
from typing import Any
from typing import Generator

from ckms.types import CipherText
from ckms.types import ClaimSet
from ckms.types import Data
from ckms.core.const import DEFAULT_CONTENT_ENCRYPTION_ALGORITHM
from ckms.core.models import ContentEncryptionKey
from ckms.utils import b64encode
from ckms.utils import b64encode_str
from ckms.utils import b64encode_json
from ckms.types import Encrypter
from ckms.types import Signer
from ckms.types.icontentencryptionkey import IContentEncryptionKey

from .recipient import Recipient
from .signature_ import Signature


class JOSEPayload:
    __module__: str = 'ckms.jose'
    _allow_compact: bool
    _allow_flattened: bool
    _aad: bytes | None = None
    _ciphertext: CipherText | None = None
    _claims: ClaimSet | None = None
    _content: bytes | None
    _content_type: str
    _direct: bool = False
    _encryption: str
    _encryption_key: ContentEncryptionKey | Encrypter
    _payload: Data
    _protected: dict[str, Any]
    _recipients: list[Recipient]
    _signatures: list[Signature]

    @property
    def aad(self) -> bytes:
        return (
            b64encode_json(self._protected)
            if not self._aad
            else b'.'.join([
                b64encode_json(self._protected),
                b64encode(self._aad)
            ])
        )

    def __init__(
        self,
        payload: dict[str, Any] | ClaimSet | Data,
        content_type: str | None = None,
        encryption: str = DEFAULT_CONTENT_ENCRYPTION_ALGORITHM,
        encryption_key: Encrypter | None = None,
        protected: dict[str, Any] | None = None,
        aad: bytes | dict[str, Any] |  None = None,
        allow_compact: bool = True,
        allow_flattened: bool = True
    ):
        """Initialize a new :class:`JOSEObject` instance.
        
        Args:
            payload: a :class:`ckms.types.ClaimSet` instance holding claims.
                This implies that the payload is a JSON Web Token (JWT).
            content_type (bytes): indicates the content type of the payload.
                If the payload is a JWT, then this defaults to ``'JWT'``.
        """
        if isinstance(payload, dict):
            payload = ClaimSet.parse_obj(payload)
        if isinstance(payload, ClaimSet):
            self._claims = payload
            payload = Data(
                buf=str.encode(payload.json(exclude_defaults=True), 'utf-8'),
                content_type=content_type or "JWT"
            )
        if isinstance(aad, dict):
            aad = b64encode_json(aad)
        self._aad = aad
        self._allow_compact = allow_compact
        self._allow_flattened = allow_flattened
        self._content = None
        self._encryption = encryption
        self._payload = payload
        self._protected = protected or {}
        self._recipients = []
        self._signatures = []
        if payload.content_type is None:
            raise ValueError("Data.content_type must not be None.")
        self._content_type = payload.content_type
        self._encryption_key = encryption_key or ContentEncryptionKey.generate(encryption)

    def add_recipient(
        self,
        *,
        encrypter: Encrypter,
        header: dict[str, Any] | None = None,
        direct: bool = False
    ) -> Recipient:
        """Encrypt the Content Encryption Key (CEK) for the given recipient.

        If Direct Encryption or Direct Key Agreement is used, set `encrypter`
        as the content encryption key if there are no other recipients.
        Otherwise, raise an exception, as there can be no multiple recipients
        when using these modes.

        The `header` parameter specifies a dictionary holding the per-recipient
        header. The set of keys in this header must be disjoint from the keys
        that are added to other headers, being at least:

        - ``typ``
        - ``enc``        
        """
        assert encrypter.algorithm is not None
        header = header or {}
        if encrypter.algorithm in ('ECDH-ES',):
            raise NotImplementedError
        if direct:
            if len(self._recipients) >= 1:
                raise ValueError(
                    "Can not use Direct Encryption or Direct Key Agreement with "
                    "more than one recipient."
                )
            if not encrypter.can_encrypt():
                raise ValueError("Key not suitable for encryption.")
            # Ensure that the _encryption matches the algorithm of the
            # key.
            self._encryption = encrypter.algorithm
            self._encryption_key = encrypter
        self._recipients.append(
            Recipient(encrypter=encrypter, header=header)
        )
        return self._recipients[-1]

    def add_signature(
        self,
        *,
        signer: Signer,
        protected: dict[str, Any] | None = None,
        header: dict[str, Any] | None = None
    ) -> Signature:
        """Sign the :class:`JOSEPayload` with the given signer."""
        if self.is_encrypted():
            raise ValueError("Signing must occur prior to encryption.")
        protected = protected or {}
        protected.setdefault('alg', signer.algorithm)
        protected.setdefault('kid', signer.kid)
        if self.is_jwt():
            protected['typ'] = self._content_type
        else:
            protected.setdefault('cty', self._content_type)
        sig = Signature(
            protected=protected,
            signer=signer,
            header=header,
            payload=self._payload
        )
        self._signatures.append(sig)
        return sig

    def can_flatten(self) -> bool:
        """Return a boolean indicating if the top-level object can be
        flattened.
        """
        return (
            not self.is_multirecipient()
            if self.is_encrypted()
            else not self.is_multisigned()
        )

    def get_payload(self) -> bytes:
        """Return the payload of a JWE or JWS."""
        # If JOSEPayload._content is None here, then there are no signers and
        # no recipients, as the add_signature() or add_recipient() methods
        # were never called.
        return self._content or b64encode(bytes(self._payload))

    def is_direct(self) -> bool:
        """Return a boolean indicating if the JWE uses either
        Direct Encryption or Direct Key Agreement.
        """
        return not isinstance(self._encryption_key, IContentEncryptionKey)

    def is_finalized(self) -> bool:
        """Return a boolean indicating if all signatories and recipients
        have executed their cryptographic operations.
        """
        return all(self._recipients) and all(map(bool, self._signatures))

    def is_nested(self) -> bool:
        """Return a boolean indicating if this is a nested object e.g.
        JWS inside JWE.
        """
        return bool(self._signatures) and bool(self._recipients)

    def is_encrypted(self) -> bool:
        """Return a boolean indicating if this object is encrypted."""
        return bool(self._recipients)

    def is_jwt(self) -> bool:
        """Return a boolean indicating if the payload is a JSON Web Token (JWT)."""
        return self._claims is not None

    def is_multirecipient(self) -> bool:
        """Return a boolean indicating if the object has multiple recipients."""
        return len(self._recipients) > 1

    def is_multisigned(self) -> bool:
        """Return a boolean indicating if the object has multiple signatures."""
        return len(self._signatures) > 1

    def is_signed(self) -> bool:
        """Return a boolean indicating if this object is signed."""
        return bool(self._signatures)

    async def serialize(
        self,
        compact: bool = False,
        flatten: bool = True,
        aad: bytes | dict[str, Any] | None = None,
        compress: bool = False,
        protected: dict[str, Any] | None = None
    ) -> str:
        """Serializes the JOSE object. Determine if there are recipients
        (object is JWE), signatures (object is JWS) or both (object is nested).
        Return a string containing the JOSE object, which will be JWS if there
        are signatures and JWE if there are recipients. If there are signatures
        and recipients, the string containing a nested object (signed then
        encrypted).

        A serialization format may be specified with the `compact` and `flattened`
        parameters. These are only availabe if there is a single signature and/or
        recipient. If `compact` is True, then JWE/JWS Compact Serialization is
        used. Otherwise, JWE/JWS Flattened Serialization is used, unless `flatten`
        is ``False``.

        If the encryption algorithm supports Authenticated Encryption with
        Associated Data (AEAD), the `aad` parameter may be used to specify
        Additional Authenticated Data (AAD).

        Additional protected header claims can be supplied with the `protected`
        parameter. The claims are added to the header of the top-level JOSE
        object (i.e. if the object is nested, the inner JWS does not receive
        the protected claims).

        The compress paramater is a boolean indicating that the payload of a
        JWE must be compressed using the DEFLATE (:rfc:`1951`) algorithm. If
        the instance is not JWE (i.e. does not have recipients), this
        parameter is ignored.
        """
        if compact and (self.is_multirecipient() or self.is_multisigned()):
            raise ValueError(
                "JWE/JWS Compact Serialization is not available when there "
                "are multiple signatures or recipients."
            )

        if compact and (aad or self._aad):
            raise ValueError(
                "Additional Authentication Data (AAD) can not be supplied with "
                "the JWE Compact Serialziation format."
            )

        if compress:
            raise NotImplementedError

        # Create all signatures and encrypt the plain text if there are reci
        obj = await self._payload.as_bytes()
        common_protected = protected or {}
        if self.is_signed():
            obj = b64encode(obj)
            signatures: list[dict[str, str]] = []
            protected = self._get_jws_protected_header(compact=compact)
            if not self.is_encrypted():
                # This object is top-level, add the shared protected header.
                protected.update(common_protected)
            for sig in self._signatures:
                await sig.sign(obj, protected=protected)
                signatures.append(sig.dict(compact=compact))
            obj = self._serialize_jws(
                obj={
                    'payload': bytes.decode(obj, 'ascii'),
                    'signatures': signatures
                },
                compact=compact,
                flatten=flatten
            )
        if self.is_encrypted():
            if isinstance(obj, str):
                obj = str.encode(obj, 'utf-8')
            recipients: list[dict[str, Any]] = []
            for recipient in self._recipients:
                await recipient.encrypt(cek=self._encryption_key) # type: ignore
                recipients.append(recipient.dict(compact=compact, flatten=flatten))

            aad = aad or self._aad
            if aad and isinstance(aad, dict):
                aad = str.encode(json.dumps(aad), 'utf-8')

            # With compact serialization, there is a single recipient
            # and its header values need to be added to the protected
            # header, since the unprotected and per-recipient headers
            # are not included in the serialization.
            if compact:
                common_protected.update(recipients[0].get('header') or {})

            protected_b64 = b64encode_json({
                **self._get_jwe_protected_header(compact=compact),
                **common_protected
            })

            assert aad is None or isinstance(aad, bytes)
            ct = await self._encryption_key.encrypt(
                pt=obj,
                aad=self._get_aad(protected_b64, aad)
            )
            obj = self._serialize_jwe(
                obj={
                    'protected': protected_b64.decode('ascii'),
                    'unprotected': {},
                    'iv': b64encode_str(ct.iv or b''),
                    'ciphertext': b64encode_str(bytes(ct)),
                    'tag': b64encode_str(ct.tag or b''),
                    'aad': b64encode_str(aad or b''),
                    'recipients': recipients
                },
                compact=compact,
                flatten=flatten
            )

        assert obj is not None
        assert isinstance(obj, str), obj
        return obj

    def _get_jwe_protected_header(self, compact: bool = False) -> dict[str, Any]:
        # The "typ" value "JOSE" can be used by applications to indicate that
        # this object is a JWS or JWE using the JWS Compact Serialization or
        # the JWE Compact Serialization.  The "typ" value "JOSE+JSON" can be
        # used by applications to indicate that this object is a JWS or JWE
        # using the JWS JSON Serialization or the JWE JSON Serialization.
        # Other type values can also be used by applications (RFC 7515, 4.1.9).
        protected = self._protected = {
            **self._protected,
            'cty': self._content_type,
            'enc': self._encryption,
            'typ': "JOSE+JSON"
        }
        if compact:
            protected['typ'] = "JOSE"

        if self.is_signed():
            protected['cty'] = "JOSE" if compact else "JOSE+JSON"

        if self.is_jwt():
            # JSON Web Tokens (JWTs) have some special rules regarding the "typ"
            # and "cty" header values.
            del protected['cty'] # cty header is only included when nesting.
            protected['typ'] = self._content_type
            if self.is_nested():
                # In the case that nested signing or encryption is employed,
                # this Header Parameter MUST be present; in this case, the
                # value MUST be "JWT", to indicate that a Nested JWT is carried
                # in this JWT.  While media type names are not case sensitive,
                # it is RECOMMENDED that "JWT" always be spelled using
                # uppercase characters for compatibility with legacy
                # implementations (RFC 7519, 5.2).
                #
                # The actual content type specified in the innner JWS.
                protected['typ'] = "JWT"
                protected['cty'] = "JWT"

        return {k: v for k, v in protected.items() if v}

    def _get_aad(self, protected: bytes, aad: bytes | None) -> bytes:
        return (
            protected
            if aad is None
            else b'.'.join([
                protected,
                b64encode(aad)
            ])
        )

    def _serialize_jwe(
        self,
        obj: dict[str, Any],
        compact: bool,
        flatten: bool
    ) -> str:
        compact = compact and self._allow_compact
        flatten = flatten and self._allow_flattened
        jwe: dict[str, Any] | str = obj
        recipients = jwe.get('recipients') or []
        if len(recipients) == 1 and (flatten or compact):
            jwe.update(jwe['recipients'][0])
            if compact:
                # This implementation always sets the protected header, holding the
                # enc and typ claims.
                jwe = (
                    f"{jwe['protected']}."
                    f"{jwe['encrypted_key']}."
                    f"{jwe.get('iv') or ''}."
                    f"{jwe['ciphertext']}."
                    f"{jwe.get('tag') or ''}"
                )
        if isinstance(jwe, dict):
            jwe = json.dumps({k: v for k, v in jwe.items() if v}, sort_keys=True)
        return jwe

    def _get_jws_protected_header(self, compact: bool = False) -> dict[str, Any]:
        protected = {'typ': "JOSE+JSON"}
        if compact:
            protected['typ'] = "JOSE"
        if self.is_jwt():
            protected['typ'] = self._content_type or "JWT"
        return protected

    def _serialize_jws(
        self,
        obj: dict[str, Any],
        compact: bool,
        flatten: bool
    ) -> str:
        compact = compact and self._allow_compact
        flatten = flatten and self._allow_flattened
        jws: dict[str, Any] | str = obj
        signatures = jws.get('signatures') or []
        if len(signatures) == 1 and (flatten or compact):
            jws.update(signatures[0])
            if 'header' in obj and not obj.get('header'):
                del jws['header']
            if compact:
                jws = f"{jws['protected']}.{jws['payload']}.{jws['signature']}"
        if not compact:
            jws = json.dumps(obj, sort_keys=True)
        assert isinstance(jws, str)
        return jws

    def __await__(self) -> Generator[Any, None, str]:
        compact = not self.is_multirecipient() and not self.is_multisigned()
        return self.serialize(compact=compact).__await__()