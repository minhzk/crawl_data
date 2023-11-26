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
        np = 0
        nv = 0
        async for product in client.listall(Product):
            print(f'{product.title} (id: {product.id})')
            np += 1
            async for variant in product.get_variants():
                print(f'  {variant.title} (id: {variant.id}, sku: {variant.sku}, inventory: {variant.inventory_item_id})')
                nv += 1
        print(f'{np} Products and {nv} ProductVariants')


if __name__ == '__main__':
    asyncio.run(main())