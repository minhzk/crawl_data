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
"""Declares :class:`JSONWebEncryption`."""
import inspect
from typing import cast
from typing import Any
from typing import Literal
from ckms.types.decrypter import Decrypter

import pydantic

from ckms.types import CipherText
from ckms.types import IKeychain
from ckms.types import IKeySpecification
from ckms.types import IProvider
from ckms.types import MalformedHeader
from ckms.types import MalformedPayload
from ckms.utils import b64decode_json
from .joseheader_ import JOSEHeader
from .octetb64 import OctetB64
from .recipient import Recipient


class JSONWebEncryption(pydantic.BaseModel):
    kind: Literal['JWE']
    token: str
    header: JOSEHeader
    protected: str = ''
    unprotected: dict[str, Any] = {}
    aad: str = ''
    ciphertext: OctetB64
    iv: OctetB64 | None
    tag: OctetB64
    recipients: list[Recipient]
    compact: bool = False

    @property
    def recipient(self) -> Recipient:
        """The first recipient in the array of recipients. Use as a
        shortcut for JWEs that have a single recipient.
        """
        return self.recipients[0]

    @pydantic.root_validator(allow_reuse=True, pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        recipients: list[dict[str, Any]] = values.get('recipients') or []
        protected = b64decode_json(
            values.get('protected') or b'',
            on_failure=MalformedHeader(
                detail=(
                    "The JWE Protected Header could not be interpreted as "
                    "a Base64-encoded JSON object."
                )
            ),
            require=dict
        )
        unprotected = dict(values.get('unprotected') or {})

        assert isinstance(protected, dict)
        if set(protected.keys()) & set(unprotected.keys()):
            raise Exception
        common_header = values['header'] = JOSEHeader.parse_obj({
            **unprotected,
            **protected
        })
        for recipient in recipients:
            header = recipient.get('header') or {}
            if not isinstance(header, dict):
                raise MalformedHeader(
                    detail=(
                        "The per-recipient header must be a JSON object."
                    )
                )

            duplicates = set(header.keys()) & set(common_header.dict(exclude_defaults=True))
            if duplicates:
                raise MalformedHeader(
                    detail=(
                        "The claims in a per-recipient header must be "
                        "disjoint from the protected and unprotected "
                        "headers."
                    ),
                    hint=(
                        "The following claims were duplicate: "
                        f"{', '.join(sorted(duplicates))}."
                    )
                )
            recipient['header'] = common_header.clone(
                values=recipient.pop('header', {})
            )

        return values

    async def decrypt(self, keychain: IKeychain) -> bytes:
        """Decrypt the payload."""
        cek = self.decrypt_cek(keychain)
        if inspect.isawaitable(cek):
            cek = await cek
        return await cek.decrypt( # type: ignore
            CipherText(
                buf=bytes(self.ciphertext),
                aad=self.get_aad(),
                iv=bytes(self.iv or b''),
                tag=bytes(self.tag)
            )
        )

    async def decrypt_cek(self, keychain: IKeychain) -> IKeySpecification:
        """Return a :class:`~ckms.types.IKeySpecification` describing the
        key that was used to encrypt the payload.
        """
        kid = self.header.kid
        cek = None
        provider = IProvider.get('local')
        spec = None

        # If direct encryption is used and the kid claim is in the header,
        # immediately look up the key and bail out (TODO: audit).
        if keychain.has(kid) and self.is_direct():
            return cast(IKeySpecification, keychain.get(kid))

        # Find any recipient for which we can decrypt the CEK or find
        # the direct encryption key.
        for recipient in self.recipients:
            kid = recipient.kid or kid
            if kid is None or not keychain.has(kid):
                continue
            spec = cast(Decrypter, keychain.get(kid))
            if not self.is_direct():
                ct = CipherText(
                    buf=recipient.encrypted_key,
                    iv=recipient.iv,
                    tag=recipient.tag
                )
                cek = spec.decrypt(ct)
                if inspect.isawaitable(cek):
                    cek = await cek
                spec = provider.parse_spec({
                    'kty': 'oct',
                    'algorithm': self.header.enc,
                    'use': 'enc',
                    'key': {'cek': cek}
                })
                await spec
            break
        else:
            raise MalformedPayload(
                detail=(
                    "No key could be found to decrypt the payload."
                )
            )
        return spec

    def get_content_type(self) -> str | None:
        """Return the content type from the ``cty`` header."""
        return str.lower(self.header.cty or '') if self.header.cty else None

    def get_type(self) -> str | None:
        """Return the object type from the ``typ`` header."""
        return str.lower(self.header.typ or '') if self.header.typ else None

    def is_direct(self) -> bool:
        """Return a boolean indicating if the JWE was encrypted in Direct
        Encryption or Direct Key Agreement mode.
        """
        # TODO: We assume here that a JWE in Direct Encryption or
        # Direct Key Agreement has only one recipient.
        if len(self.recipients) != 1:
            return False
        return self.recipient.alg == 'dir'

    def get_aad(self) -> bytes | None:
        """Return the the Additional Authenticated Data (AAD) for AEAD
        encryption algorithms.
        """
        aad = str.encode(self.protected or '', 'ascii')
        #if self.aad:
        #    aad += b'.' + b64encode(self.aad)
        return aad

    def get_headers(self) -> list[JOSEHeader]:
        """Return the list of :class:`JOSEHeader` containing the aggregated
        header claims for all recipients.
        """
        return [x.header for x in self.recipients]