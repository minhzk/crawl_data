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
from headless.ext.picqer import PurchaseOrder


async def main():
    params = {
        'api_key': os.environ['PICQER_API_KEY'],
        'api_email': 'test@headless.python.dev.unimatrixone.io',
        'api_url': os.environ['PICQER_API_URL']
    }
    async with Client(**params) as client:
        orders: list[PurchaseOrder] = [x async for x in client.list(PurchaseOrder)]
        if not orders:
            print("You needs at least one purchase order for this example to work.")
            raise SystemExit
        order = orders[0]

        # Before awaiting, the attribute contains a wrapper.
        print(repr(order.supplier))

        # After awaiting the object, the resource becomes available.
        await order.supplier
        print(repr(order.supplier))

        # Resource objects can also be awaited so that you dont have
        # to check if the attribute was already fetched.
        print(repr(await order.supplier))



if __name__ == '__main__':
    asyncio.run(main())