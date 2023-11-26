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

from headless.ext.shopify import AdminClient
from headless.ext.shopify.v2023_1 import Order


async def main():
    params = {
        'access_token': os.environ['SHOPIFY_ACCESS_TOKEN'],
        'domain': os.environ['SHOPIFY_SHOP_DOMAIN']
    }

    # Retrieve all Order resources for the configured shop and
    # print the total outstanding amount.
    async with AdminClient(**params) as client:
        async for order in client.listall(Order):
            print(f'Order (#{order.number}): {order.currency} {order.total_outstanding}')



if __name__ == '__main__':
    asyncio.run(main())