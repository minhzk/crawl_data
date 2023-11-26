# Copyright (C) 2023 Cochise Ruhulessin
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
from typing import TypeVar

from pydantic.validators import str_validator

from headless.types import ICredential
from headless.types import IRequest


T = TypeVar('T', bound='BearerTokenCredential')


class BearerTokenCredential(ICredential):
    __module__: str = 'headless.ext.oauth2.types'
    __value: str

    @classmethod
    def __get_validators__(cls: type[T]) -> Generator[Callable[..., str | T], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls: type[T], v: str) -> T:
        return cls(v)

    def __init__(self, value: str):
        self.__value = value

    async def add_to_request(self, request: IRequest[Any]) -> None:
        request.add_header('Authorization', f'Bearer {self.__value}')

    def __repr__(self) -> str:
        return 'BearerTokenCredential(***)'

    def __str__(self) -> str:
        return self.__value