# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Generator

import pytz
from pydantic.validators import str_validator


TIMEZONES: list[str] = [x for x in pytz.all_timezones if '/' in x] # type: ignore


class TimezoneInfo(str):

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title='Timezone',
            type='string',
            format='string'
        )

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if len(v) > 128:
            raise ValueError("Value is too long to be a valid time zone.")
        if v not in TIMEZONES:
            raise ValueError(f"Not a valid time zone: {v}")
        return cls(v)

    def __repr__(self) -> str: # pragma: no cover
        return f'EmailAddress({self})'