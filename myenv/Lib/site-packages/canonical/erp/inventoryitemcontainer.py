# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import decimal

import pydantic


class InventoryItemContainer(pydantic.BaseModel):
    """Specifies a location in which an inventory item can be stored.
    
    The :class:`InventoryItemContainer` entity can describe fixed
    locations, such as a rack, room or warehouse; or mobile
    containers such as a bin, trolley, vehicle or ship.
    """
    id: int = pydantic.Field(
        default=...,
        title="Container ID",
        description="Identifies the container.",
        primary_key=True
    )

    label: str = pydantic.Field(
        default='',
        title="Label",
        description="A human-readable name for this Container."
    )

    contained_by: int | None = pydantic.Field(
        default=...,
        title="Contained by",
        description="The parent container."
    )

    #: Tree model

    #: Physical properties
    empty_weight: decimal.Decimal = pydantic.Field(
        default=0,
        title="Weight",
        description="The empty weight of the container, in kilograms."
    )

    #: Physical constraints
    wll: decimal.Decimal | None = pydantic.Field(
        default=None,
        title="Working Load Limit (WLL)",
        description=(
            "The maximum amount of load that can be applied/stored to "
            "the container. This is provided by either the manufacturer "
            "or benchmarked by the user. In kilograms."
        )
    )