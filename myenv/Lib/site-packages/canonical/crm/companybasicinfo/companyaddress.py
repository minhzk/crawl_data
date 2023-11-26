# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from canonical import GenericDeliveryPointSpecification
from canonical import GenericPostalAddress


class CompanyAddress(pydantic.BaseModel):
    kind: Literal['visiting', 'invoicing'] | None = pydantic.Field(
        default=None,
        title="Kind",
        description=(
            "Specifies the kind of address, or `null` if no specific "
            "kind is known for this address."
        )
    )

    spec: GenericPostalAddress | GenericDeliveryPointSpecification = pydantic.Field(
        default=...,
        title="Specification",
        description=(
            "Contains the companies' address as a `GenericPostalAddress` or "
            "`GenericDeliveryPointSpecification` object."
        )
    )

    class Config:
        allow_population_by_field_name: bool = True