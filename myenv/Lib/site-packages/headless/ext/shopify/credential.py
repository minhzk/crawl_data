# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from headless.types import ICredential
from headless.types import IRequest


class ShopifyCredential(ICredential):
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    async def add_to_request(self, request: IRequest[Any]) -> None:
        request.add_header('X-Shopify-Access-Token', self.access_token)