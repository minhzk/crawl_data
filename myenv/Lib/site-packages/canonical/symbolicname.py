# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from types import EllipsisType
from typing import Any
from typing import Callable
from typing import Generator
from typing import Pattern
from typing import TypeVar

from pydantic.validators import str_validator


T = TypeVar('T')


class SymbolicNameMetaclass(type):

    def __getitem__(
        self: T,
        opts: int | tuple[
            EllipsisType | int | None,
            EllipsisType | int | None,
            EllipsisType | str | None,
        ],
    ) -> T:
        min_length: int | EllipsisType | None = 6
        max_length: int | EllipsisType | None = 31
        pattern: None | Pattern[str] = re.compile('^[a-z][a-z0-9\\-]+[a-z0-9]$')
        if isinstance(opts, int):
            max_length = opts
        elif len(opts) >= 2:
            min_length, max_length, *remaining = opts
            if remaining:
                if isinstance(remaining[0], str):
                    pattern = re.compile(remaining[0])
                elif remaining[0] is None:
                    pattern = None
        if min_length == ...:
            min_length = 6
        if min_length is None:
            min_length = 0
        if max_length == ...:
            max_length = 31
        if max_length is None:
            max_length = 0
        assert min_length < max_length # nosec
        return type(self.__name__, (self,), { # type: ignore
            'min_length': min_length,
            'max_length': max_length,
            'pattern': pattern
        })


class SymbolicName(str, metaclass=SymbolicNameMetaclass):
    min_length: int = 6
    max_length: int = 31
    pattern: Pattern[str] | None = re.compile('^[a-z][a-z0-9\\-]+[a-z0-9]$')

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title='Symbolic Name',
            type='string',
        )

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if cls.min_length and len(v) < cls.min_length:
            raise ValueError("Symbolic name is too short.")
        if cls.max_length and len(v) > cls.max_length:
            raise ValueError("Symbolic name is too long.")
        if cls.pattern and not cls.pattern.match(v):
            raise ValueError("Invalid characters.")
        return cls(v)

    def __repr__(self) -> str: # pragma: no cover
        return f'SymbolicName({self})'