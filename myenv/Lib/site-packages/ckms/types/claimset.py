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
"""Declares :class:`ClaimSet`."""
import json
from typing import Any
from typing import Generator
from typing import Iterable

import pydantic

from ckms.types import AudienceType
from ckms.utils import b64encode
from ckms.utils import b64decode_json
from .malformed import ClaimTypeError
from .malformed import MalformedPayload
from .malformed import MissingRequiredClaim


class ClaimSet(pydantic.BaseModel):
    __module__: str = 'ckms.types'
    _strict_required: set[str] = set()
    _extra: dict[str, Any] = pydantic.PrivateAttr(default={})

    @property
    def extra(self) -> dict[str,Any]:
        return self._extra

    @classmethod
    def fromjson(cls, payload: bytes | str) -> 'ClaimSet':
        try:
            if isinstance(payload, bytes):
                payload = bytes.decode(payload, 'utf-8')
            return cls.parse_obj(
                json.loads(payload)
            )
        except (ValueError, TypeError):
            raise MalformedPayload

    @classmethod
    def frompayload(cls, payload: bytes | str) -> 'ClaimSet':
        return cls.parse_obj(
            b64decode_json(
                buf=payload,
                on_failure=MalformedPayload()
            )
        )

    @classmethod
    def strict(cls, **claims: Any) -> 'ClaimSet':
        raise NotImplementedError

    def __init__(self, **claims: Any):
        try:
            extra = claims.pop('extra', {})
            super().__init__(**claims)
            for name, value in claims.items():
                if name in self.__fields__:
                    continue
                extra[name] = value
            self._extra = extra
        except pydantic.ValidationError as exception:
            for error in exception.errors():
                error_type = error.get('type') or ''
                if str.startswith(error_type, 'type_error'):
                    claim = error['loc'][0]
                    raise ClaimTypeError(str(claim)) from exception
            else:
                raise

    def clone(self, values: dict[str, Any]) -> 'ClaimSet':
        """Clone the claims set with the updated `values`."""
        return type(self).parse_obj({
            **self.dict(),
            **values
        })

    def dict(self, **kwargs: Any) -> dict[str, Any]: # type: ignore
        kwargs.setdefault('exclude_defaults', True)
        return super().dict(**kwargs)

    def json(self, **kwargs: Any) -> str: # type: ignore
        kwargs.setdefault('exclude_defaults', True)
        return super().json(**kwargs)

    def verify(
        self,
        *,
        required: set[str] | None = None,
        strict: bool = False,
    ) -> None:
        """Verifies the claims according to the specification laid out
        in the JOSE RFCs.
        """
        required = required or set()
        if strict:
            required.update(self._strict_required)
        for claim in required:
            if getattr(self, claim, self.extra.get(claim)) is not None:
                continue
            raise MissingRequiredClaim(claim)

    def _iter(self, **kwargs: Any) -> Generator[tuple[str, Any], None, None]:
        for name, value in super()._iter(**kwargs):
            if name != 'extra':
                yield name, value
                continue
        for extra_claim, extra_value in self.extra.items():
            yield extra_claim, extra_value

    def __bytes__(self) -> bytes:
        return b64encode(self.json())

    def __xor__(self, value: set[str] | Iterable[Any]) -> set[str]:
        if not isinstance(value, set):
            value = set(value)
        return set(self.__fields__.keys()) ^ value

    def __rxor__(self, value: set[str]) -> set[str]:
        return self.__xor__(value)

    class Config:
        json_encoders: dict[type[Any], Any] = {
            AudienceType: lambda aud: list(sorted(aud)) # type: ignore
        }