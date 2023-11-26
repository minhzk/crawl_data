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
"""Declares :class:`JSONWebSignature`."""
import asyncio
import hashlib
from typing import Any
from typing import Literal

import pydantic

from ckms.types import IKeychain
from ckms.types import JSONWebToken
from ckms.types import MalformedHeader
from ckms.types import MalformedPayload
from ckms.utils import b64decode_json
from .octetb64 import OctetB64
from .joseheader_ import JOSEHeader
from .signature import Signature


class JSONWebSignature(pydantic.BaseModel):
    kind: Literal['JWS'] = pydantic.Field(..., exclude=True)
    token: str
    payload: str
    signatures: list[Signature]

    @property
    def cty(self) -> str | None:
        """The type of JOSE object as defined by the ``cty`` claim."""
        return str.lower(self.header.cty) if self.header.cty else None

    @property
    def header(self) -> JOSEHeader:
        """The header of the first signature. The claims presented in this
        header are considered authoritative when determining the type,
        content type.
        """
        return self.signatures[0].header

    @property
    def typ(self) -> str | None:
        """The type of JOSE object as defined by the ``typ`` claim."""
        return str.lower(self.header.typ) if self.header.typ else None

    @pydantic.root_validator(pre=True, allow_reuse=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        for signature in (values.get('signatures') or []):
            protected = b64decode_json(
                signature.get('protected') or b'{}',
                on_failure=MalformedHeader(
                    detail=(
                        "The JWE Protected Header could not be interpreted as "
                        "a Base64-encoded JSON object."
                    )
                ),
                require=dict
            )

            assert isinstance(protected, dict)
            header = signature.get('header') or {}

            # The Header Parameter values used when creating or validating
            # individual signature or MAC values are the union of the two
            # sets of Header Parameter values that may be present: (1) the
            # JWS Protected Header represented in the "protected" member of
            # the signature/MAC's array element, and (2) the JWS Unprotected
            # Header in the "header" member of the signature/MAC's array element.
            # The union of these sets of Header Parameters comprises the JOSE
            # Header.  The Header Parameter names in the two locations MUST
            # be disjoint (RFC7515, 7.2.1).
            duplicates = set(protected.keys()) & set(header.keys())
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

            signature['header'] = {**header, **protected}

        return values

    def claims(self, accept: set[str]) -> JSONWebToken:
        """Return the claims set included in the JWS. If the JWS is not a JWT,
        raise an exception.
        """
        if self.typ not in accept:
            raise MalformedPayload(
                detail=(
                    "The JSON Web Signature (JWS) does not include a "
                    "claims set of an accepted type."
                )
            )
        return JSONWebToken.frompayload(self.payload)

    def digest(self, name: str = 'sha3_256') -> bytes:
        """Return a hash of the payload."""
        return hashlib.new(name, self.payload.encode('ascii')).digest()

    def hexdigest(self, *args: Any, **kwargs: Any) -> str:
        """Return a hex-encoded hash of the payload."""
        return self.digest().hex()

    def get_claims(self, model: type[JSONWebToken] = JSONWebToken):
        """Return the claims signed by the JWS."""
        return model.frompayload(self.payload)

    def get_headers(self) -> list[JOSEHeader]:
        """Return the list of :class:`JOSEHeader` containing the aggregated
        header claims for all signatures.
        """
        return [x.header for x in self.signatures]

    def get_payload(self) -> bytes:
        """Return the payload of te JWS."""
        return self.payload.encode('ascii')

    def get_type(self) -> str | None:
        """Return the normalized type of the JWS."""
        header = self.signatures[0].header
        return str.lower(header.typ or '') if header.typ else None

    def is_jwt(self, accept: set[str] = {"at+jwt", "jwt", "secevent+jwt"}) -> bool:
        """Return a boolean indicating if the :class:`JSONWebSignature` is
        a JSON Web Token (JWT).
        """
        return str.lower(self.signatures[0].header.typ or '') in accept

    async def verify(
        self,
        keychain: IKeychain,
        require_kid: bool = True
    ) -> bool:
        """Verify the JSON Web Signature (JWS) using the given
        :class:`~ckms.core.types.IKeychain` implementation
        `keychain`.
        """
        results = await asyncio.gather(*[
            x.verify(keychain, self.payload, require_kid=require_kid)
            for x in self.signatures
        ])
        return bool(results) and all(results)

    class Config:
        json_encoders: dict[Any, Any] = {
            bytes: lambda value: value.decode('ascii'), # type: ignore
            OctetB64: OctetB64.serialize
        }
