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
"""Declares :class:`AudienceType`"""
from typing import Any
from typing import Generator
from typing import TypeAlias

from .malformed import ClaimTypeError


VALID_TYPES: TypeAlias = str | set[str] | None


class AudienceType(set[str]):
    __module__: str = "ckms.types"

    @classmethod
    def __get_validators__(
        cls
    ) -> Generator[Any, Any, Any]:
        yield cls.validate

    @classmethod
    def validate(cls,
        value: VALID_TYPES
    ) -> 'AudienceType':
        if isinstance(value, str):
            value = {value}
        if not all([isinstance(x, str) for x in value]): # type: ignore
            raise ClaimTypeError(
                claim='aud',
                hint=(
                    "The 'aud' claim is either a string or an array of strings."
                )
            )
        return cls(value or {})

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None: # pragma: no cover
        field_schema.update(
            type="array",
            examples=[
                "https://oauth2.unimatrixapis.com",
                ["https://oauth2.unimatrixapis.com"]
            ]
        )

    def __repr__(self) -> str:
        return repr(set(self))