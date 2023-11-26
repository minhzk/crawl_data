# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical import EmailAddress
from canonical import Phonenumber


class OrganizationQualifiedContact(pydantic.BaseModel):
    """A reference to a contact inside an organization. At least the email
    address and the last name must be known.
    """
    first_name: str = pydantic.Field(
        default=...,
        alias='firstName',
        title="First name"
    )

    last_name: str = pydantic.Field(
        default=...,
        alias='lastName',
        title="Last name",
    )

    email: EmailAddress = pydantic.Field(
        default=...,
        title="Email address"
    )

    phonenumber: Phonenumber  = pydantic.Field(
        default=...,
        title="Phonenumber"
    )

    class Config:
        allow_population_by_field_name: bool = True