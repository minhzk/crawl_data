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

import phonenumbers
from pydantic.validators import str_validator


class Phonenumber(str):

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update(
            format='phonenumber',
            title="Phonenumber",
            type="string",
            examples=['+31612345678'],
        )

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")
        try:
            p = phonenumbers.parse(v)
            if not phonenumbers.is_valid_number(p):
                raise ValueError("Not a valid phonenumber.")
        except (phonenumbers.NumberParseException, TypeError):
            raise ValueError("Not a valid phonenumber.")
        return cls(
            phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
        )

    def __repr__(self) -> str:
        return f'Phonenumber({self})'