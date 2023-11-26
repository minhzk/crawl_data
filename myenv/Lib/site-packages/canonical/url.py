# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from typing import cast
from typing import TypeVar
import urllib.parse

from .domainname import DomainName
from .stringtype import StringType


T = TypeVar('T', bound='URL')


class URL(StringType):
    _parse_result: urllib.parse.ParseResult
    patterns: list[re.Pattern[str]] = [
        re.compile(r'(http|https)://.*')
    ]

    def __new__(
        cls: type[T],
        object: str,
        result: urllib.parse.ParseResult | None = None
    ) -> T:
        self = super().__new__(cls, object)
        if result is None:
            # Was not created by pydantic
            for validator in cls.__get_validators__():
                self = validator(self)
        else:
            assert result is not None
            self._parse_result = result
        return cast(T, self)
    
    @classmethod
    def validate(cls, v: str) -> str:
        p = urllib.parse.urlparse(v)
        if p.scheme not in {'http', 'https'}:
            raise ValueError(f"invalid protocol for URL: {p.scheme}.")
        for validator in DomainName.__get_validators__():
            validator(p.netloc)
        return cls(v, result=p)
    
    def __repr__(self) -> str:
        return f'URL({self})'