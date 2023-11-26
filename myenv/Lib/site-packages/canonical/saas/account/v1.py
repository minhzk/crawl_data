# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical import dto
from canonical import GenericDeliveryPointSpecification
from canonical import EuropeanVatNumber
from canonical.crm import OrganizationQualifiedContact


class AccountSpec(pydantic.BaseModel):
    organization_name: str = pydantic.Field(
        default=...,
        alias='organizationName',
        title="Organization name",
        description="The company or company division name.",
        max_length=63
    )

    organization_contact: OrganizationQualifiedContact = pydantic.Field(
        default=...,
        alias='organizationContact',
        title="Contact",
        description=(
            "Contact person within the organization that is responsible for this "
            "account."
        )
    )

    business_address: GenericDeliveryPointSpecification = pydantic.Field(
        default=...,
        alias='businessAddress',
        title="Business address",
        description="The account's business address information."
    )

    vat_number: EuropeanVatNumber | None = pydantic.Field(
        default=None,
        alias='vatNumber',
        title="VAT number",
        description=(
            "The VAT number as used in the European Union (EU) or "
            "the United Kingdom (UK)."
        )
    )

    class Config:
        allow_population_by_field_name: bool = True
        title = 'AccountSpecV1'


class Account(dto.DTO, version='v1'):
    spec: AccountSpec