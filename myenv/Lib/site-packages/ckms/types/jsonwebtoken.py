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
import secrets
from typing import cast
from typing import Any

import pydantic

from ckms.utils import current_timestamp
from .audiencetype import AudienceType
from .claimset import ClaimSet
from .invalidtoken import MaximumAgeExceeded
from .invalidtoken import TokenNotEffective
from .invalidtoken import TokenExpired
from .invalidtoken import WrongAudience
from .invalidtoken import WrongIssuer


class JSONWebToken(ClaimSet):
    __module__: str = 'ckms.types'
    _strict_required: set[str] = {'jti', 'exp', 'iat', 'nbf'}
    iss: str | None = None
    sub: str | None = None
    aud: AudienceType = AudienceType()
    exp: int | None = None
    nbf: int | None = None
    iat: int | None = None
    jti: str | None = None

    @classmethod
    def fromjson(cls, payload: bytes | str) -> 'JSONWebToken':
        return cast(cls, super().fromjson(payload))

    @classmethod
    def frompayload(cls, payload: bytes | str) -> 'JSONWebToken':
        return cast(cls, super().frompayload(payload))

    @classmethod
    def strict(
        cls,
        *,
        iss: str,
        ttl: int,
        jti: str | None = None,
        **claims: Any
    ) -> 'JSONWebToken':
        now = current_timestamp()
        exp = now + ttl
        nbf = claims.setdefault('nbf', now)
        if nbf > exp:
            raise ValueError("The 'nbf' claim must not be in the future.")
        return cls.parse_obj({
            **claims,
            'iss': iss,
            'iat': now,
            'exp': exp,
            'jti': jti or secrets.token_urlsafe(24)
        })

    def add_audience(self, audience: str) -> None:
        """Adds an audience to the JSON Web Token (JWT)."""
        self.aud.add(audience)

    def expires_in(
        self,
        ttl: int | None = None,
        now: int | None = None
    ) -> int | None:
        """Set the time-to-live using the ``exp`` claim. Return
        the remaining seconds.
        """
        now = now if now is not None else current_timestamp()
        if ttl is not None:
            self.exp = now + ttl
        return (self.exp - now) if self.exp else None

    def is_selfsigned(self) -> bool:
        """Return a boolean indicating if the token is self-issuer."""
        return self.iss == self.sub and None not in {self.iss, self.sub}

    def verify(
        self,
        *,
        issuer: str | None = None,
        audience: set[str] | None = None,
        required: set[str] | None = None,
        now: int | None = None,
        max_age: int | None = None,
        strict: bool = False
    ) -> None:
        """Verifies the claims according to the specification laid out
        in the JOSE RFCs.
        """
        required = required or set()
        if max_age:
            required.add('iat')
        super().verify(required=required, strict=strict)
        now = now or current_timestamp()
        if self.exp is not None and self.exp <= now:
            raise TokenExpired
        if self.nbf and self.nbf > now:
            raise TokenNotEffective
        if audience and not bool(audience & self.aud):
            raise WrongAudience(allowed=audience)
        if max_age is not None and (now - cast(int, self.iat)) >= max_age:
            assert self.iat is not None
            raise MaximumAgeExceeded(max_age, now, self.iat)
        if issuer is not None and issuer != self.iss:
            raise WrongIssuer


class SecurityEventToken(JSONWebToken):
    """Represents a Security Event Token (SET as defined in :rfc:`8417`."""
    # RFC 8417 Security Event Token (SET)
    iss: str
    iat: int
    jti: str = pydantic.Field(
        default_factory=lambda: secrets.token_urlsafe(24),
    )
    aud: AudienceType
    exp: None
    nbf: None
    events: dict[str, dict[str, Any]]
    toe: int | None
    txn: str | None