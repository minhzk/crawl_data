# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import os

from headless.ext.picqer import Client
from headless.ext.picqer import Picklist
from headless.ext.picqer import Product


async def main():
    params = {
        'api_key': os.environ['PICQER_API_KEY'],
        'api_email': 'test@headless.python.dev.unimatrixone.io',
        'api_url': os.environ['PICQER_API_URL']
    }
    async with Client(**params) as client:
        async for p in client.list(Picklist):
            if not p.is_open():
                continue
            print(f'Picklist {p.picklistid}: {p.deliveryname}')
            for item in p.products:
                product = await client.retrieve(Product, item.idproduct)
                print(f'\tProduct {product.productcode}: {product.name}')
                if str.lower(product.get_product_field(2603) or '') == 'iphone':
                    print("\tBij verzending moet voor dit product diens IMEI worden gescand.")
                    print()
            break

if __name__ == '__main__':
    asyncio.run(main())