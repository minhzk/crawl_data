# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import logging
import os
from typing import Any

from headless.ext.shopify import AdminClient
from headless.ext.shopify.v2023_1 import Product


async def main():
    logger: logging.Logger = logging.getLogger('headless.client')
    logger.setLevel(logging.INFO)
    params: dict[str, Any]  = {
        'access_token': os.environ['SHOPIFY_ACCESS_TOKEN'],
        'domain': os.environ['SHOPIFY_SHOP_DOMAIN']
    }
    async with AdminClient(**params) as client:
        async for product in client.listall(Product):
            async for variant in product.get_variants():
                print(f'{variant.title} (id: {variant.id}, sku: {variant.sku}, inventory: {variant.inventory_item_id})')
                await variant.set_inventory_level(75206590777, 400)
                break
            break


if __name__ == '__main__':
    asyncio.run(main())