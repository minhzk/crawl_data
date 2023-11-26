# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .productidentifier import ProductIdentifierType
from .productinventorytype import ProductInventoryType


class BaseProduct(pydantic.BaseModel):
    product_name: str = pydantic.Field(
        default=...,
        title="Name",
        description=(
            "The internal name for this Product. If there is no distinction "
            "between marketed names and internal names, this may also be "
            "the marketed name."
        )
    )

    identifiers: list[ProductIdentifierType] = pydantic.Field(
        default=[],
        title="Identifiers",
        description=(
            "The known identifiers for this product, such as stock keeping "
            "unit (SKU), ISBN, EAN, model number, etc."
        )
    )

    inventory_type: ProductInventoryType = pydantic.Field(
        default=...,
        title="Inventory type",
        alias='inventoryType',
        description=(
            "Specifies the inventory type of the product. Must be "
            "`NOT_APPLICABLE` if the product is a `SERVICE`."
        )
    )