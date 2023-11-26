# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ..resource import ShopifyResource
from .inventorylevel import InventoryLevel


class ProductVariant(ShopifyResource):
    id: int
    product_id: int
    sku: str
    title: str
    inventory_item_id: int

    async def set_inventory_level(
        self,
        location_id: int,
        available: int
    ) -> InventoryLevel:
        """Set the inventory level at the given location."""
        level = InventoryLevel(
            location_id=location_id,
            inventory_item_id=self.inventory_item_id,
            available=available
        )
        return await level.persist(self._client)

    class Meta:
        base_endpoint: str = '/2023-01/products/{0}/variants'
        name: str = 'variant'
        pluralname: str = 'variants'