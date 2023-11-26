# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied
import datetime
import urllib.parse
from typing import Any
from typing import Callable
from typing import TypeVar

import pydantic

from canonical import DomainName
from canonical import EmailAddress
from canonical import Phonenumber
from canonical import ResourceName
from .v1 import CompanyBasicInfoV1


T = TypeVar('T')


class CompanyBasicInfo(pydantic.BaseModel):
    """A Data Transfer Object (DTO) model to exchange basic information
    about companies.
    """
    __root__: CompanyBasicInfoV1

    @classmethod
    def parse(
        cls,
        *,
        name: ResourceName,
        spec: dict[str, Any],
        version: str | None = None,
        annotations: dict[str, str] | None = None,
        labels: dict[str, str] | None = None,
        tags: set[str] | None = None
    ):
        params: dict[str, Any] = {
            'kind': cls.__name__,
            'metadata': {
                'name': name,
                'annotations': annotations or {},
                'labels': labels or {},
                'tags': tags or set()
            },
            'spec': spec
        }
        if version is not None:
            params['apiVersion'] = version
        return cls.parse_obj(params)
    
    @property
    def domain(self) -> DomainName | None:
        """Return the domain name of the website, or ``None``."""
        if self.spec.website is not None:
            p = urllib.parse.urlparse(self.spec.website)
            return DomainName(p.netloc)

    @property
    def name(self) -> ResourceName:
        return self.__root__.metadata.name

    @property
    def phone(self) -> Phonenumber:
        phonenumbers = self.__root__.spec.phonenumbers
        if not phonenumbers:
            raise AttributeError(
            f"Company does not have a phonenumber (name: {self.name})"
            )
        if len(phonenumbers) > 1:
            raise AttributeError(
            f"Company has multiple phonenumbers (name: {self.name})"
            )
        return phonenumbers[0].value

    @property
    def spec(self):
        return self.__root__.spec

    def annotate(self, name: str, value: Any, namespace: str | None = None) -> None:
        qualname = name
        if namespace is not None:
            qualname = f'{namespace}/{name}'
        self.__root__.metadata.annotations[qualname] = value

    def get_annotation(
        self,
        name: str,
        parser: Callable[[str], T] = str,
        namespace: str | None = None
    ) -> None | T:
        """Get and parse the given annotation."""
        qualname = name
        if namespace is not None:
            qualname = f'{namespace}/{name}'
        value = self.__root__.metadata.annotations.get(qualname)
        if value is not None:
            value = parser(value)
        return value

    def add_email(
        self,
        source: DomainName | ResourceName,
        email: EmailAddress,
        obtained: datetime.datetime | None = None
    ) -> None:
        """Add an email address to this company."""
        if self.has_email(email):
            raise ValueError(f'Email {email} is already known for {self.name}')
        self.__root__.add_email(source, email, obtained)

    def get_tags(self) -> set[str]:
        """Return the set of tags that this resource was tagged with."""
        return self.__root__.metadata.tags

    def has_annotation(self, name: str, namespace: str | None = None) -> bool:
        """Return a boolean indicating if the resource has the given
        annotation.
        """
        qualname = name
        if namespace is not None:
            qualname = f'{namespace}/{name}'
        return qualname in self.__root__.metadata.annotations

    def has_email(self, email: EmailAddress | None = None) -> bool:
        """Return a boolean indicating if at least one email address
        is known for the company, if `email` is ``None``, otherwise
        return a boolean indicating if `email` is known.
        """
        if email is not None:
            return any([x.value == email for x in self.spec.email_addresses])
        return len(self.spec.email_addresses) > 0

    def has_phonenumber(self) -> bool:
        """Return a boolean indicating if at least one phone number
        is known for the company.
        """
        return len(self.spec.phonenumbers) > 0

    def has_website(self) -> bool:
        """Return a boolean indicating if the website is known for the company."""
        return bool(self.spec.website)

    class Config:
        allow_population_by_field_name: bool = True