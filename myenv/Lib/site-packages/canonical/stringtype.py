# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import hashlib
import re
from typing import Any
from typing import Callable
from typing import Generator

from pydantic.validators import str_validator


class StringType(str):
    """Base class for string types."""
    __module__: str = 'canonical'
    openapi_title: str | None = None
    openapi_format: str | None = None
    max_length: int | None = None
    min_length: int | None = None
    patterns: re.Pattern[Any] | list[re.Pattern[Any]] = []
    __value: str

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title=cls.openapi_title or cls.__name__,
            type='string'
        )
        if cls.openapi_format:
            field_schema.update(format=cls.openapi_format)

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        if cls.patterns:
            yield cls.validate_pattern
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if cls.max_length and len(v) > cls.max_length:
            raise ValueError(f"too long to be a valid {cls.__name__}.")
        if cls.min_length and len(v) < cls.min_length:
            raise ValueError(f"too short to be a valid {cls.__name__}.")
        return cls(v)

    @classmethod
    def validate_pattern(cls, v: str) -> str:
        patterns = cls.patterns
        if not isinstance(patterns, list):
            patterns = [patterns]
        for pattern in patterns:
            if not pattern.match(v):
                raise ValueError(f"not a valid {cls.__name__}.")
        return v

    def sha256(self) -> str:
        h = hashlib.sha3_256()
        h.update(str.encode(type(self).__name__))
        h.update(str.encode(self, encoding='utf-8'))
        return h.hexdigest()

    def __repr__(self) -> str: # pragma: no cover
        return f'{type(self).__name__}({self})'