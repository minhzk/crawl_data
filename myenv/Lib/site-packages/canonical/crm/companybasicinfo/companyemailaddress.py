# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Literal

import pydantic

from canonical import DomainName
from canonical import ResourceName
from canonical import EmailAddress
from canonical import URL


class CompanyEmailAddress(pydantic.BaseModel):
    kind: Literal['general'] | None = pydantic.Field(
        default=None,
        title="Kind",
        description=(
            "Specifies the kind of email address, or `null` if no specific "
            "kind is known for this mailbox."
        )
    )

    value: EmailAddress = pydantic.Field(
        default=...,
        title="Value",
        description="Contains the companies' email address."
    )

    source: URL | ResourceName | DomainName = pydantic.Field(
        default=...,
        title="Source",
        description=(
            "Indicates the source from which the email address was obtained."
        )
    )

    obtained: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Obtained",
        description=(
            "Describes the date and time at which the email address was "
            "obtained from the `source`."
        )
    )

    class Config:
        allow_population_by_field_name: bool = True