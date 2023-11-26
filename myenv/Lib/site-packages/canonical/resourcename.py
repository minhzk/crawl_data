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

from .domainname import DomainName
from .stringtype import StringType


T = TypeVar('T', bound='ResourceName')


class ResourceName(StringType):
    relname: str
    service: DomainName
    patterns: list[re.Pattern[str]] = [
        re.compile(r'//.*')
    ]

    @property
    def id(self) -> str:
        return str.split(self, '/')[-1]

    @classmethod
    def null(cls: type[T]) -> T:
        """Return an instance that represents an unassigned
        resource name.
        """
        return cls('//cochise.io/resources/null')

    def __new__(
        cls: type[T],
        object: str,
        service: DomainName | None = None,
        relname: str | None = None
    ) -> T:
        self = super().__new__(cls, object)
        if service is None:
            # Was not created by pydantic
            for validator in cls.__get_validators__():
                self = validator(self)
        else:
            assert relname is not None
            self.relname = relname
            self.service = service
        return cast(T, self)
    
    @classmethod
    def validate(cls, v: str) -> str:
        assert str.startswith(v, '//')
        service, _, relname = str.partition(v[2:], '/')
        if not relname:
            raise ValueError("a valid ResourceName contains a relative name.")
        for validator in DomainName.__get_validators__():
            service = validator(service)
        return cls(v, relname=relname, service=DomainName(service))