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
from typing import Awaitable

from headless.ext.shopify import AdminClient
from headless.ext.shopify.v2023_1 import Order


async def main():
    params = {
        'access_token': os.environ['SHOPIFY_ACCESS_TOKEN'],
        'domain': os.environ['SHOPIFY_SHOP_DOMAIN']
    }
    async with AdminClient(**params) as client:
        orders: list[Order] = [x async for x in client.list(Order)]
        if not orders:
            print("Your shop needs at least one order for this example to work.")
            raise SystemExit
        requests: list[Awaitable[Order]] = []

        # The Shopify Admin API limits the request to 40 per minute,
        # but the code below will not raise any errors related to
        # rate limiting.
        for _ in range(60):
            requests.append(client.retrieve(Order, orders[0].id))
        orders = await asyncio.gather(*requests)


if __name__ == '__main__':
    asyncio.run(main())