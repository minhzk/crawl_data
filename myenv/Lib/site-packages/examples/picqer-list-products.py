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
from headless.ext.picqer import Product


async def main():
    params = {
        'api_key': os.environ['PICQER_API_KEY'],
        'api_email': 'test@headless.python.dev.unimatrixone.io',
        'api_url': os.environ['PICQER_API_URL']
    }
    async with Client(**params) as client:
        n = 0
        async for product in client.listall(Product):
            n += 1
            print(f'Product {product.productcode}: {product.name}')
            if str.lower(product.get_product_field(2603) or '') in ('iphone', 'samsung'):
                print("\tBij verzending moet voor dit product diens IMEI worden gescand.")

        print(f'Listed {n} Products')




if __name__ == '__main__':
    asyncio.run(main())