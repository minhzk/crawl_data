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

from pydantic.validators import str_validator
from pydantic.networks import validate_email

from .domainname import DomainName


class EmailAddress(str):

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title='Email Address',
            type='string',
            format='email'
        )

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if len(v) > 320:
            raise ValueError("Value is too long to be a valid email address.")
        v = str.lower(v)
        return cls(validate_email(v)[1]) # type: ignore

    @property
    def domain(self) -> DomainName:
        return DomainName(str.split(self, '@')[-1])

    def __repr__(self) -> str: # pragma: no cover
        return f'EmailAddress({self})'