# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import AsyncGenerator

from ..resource import ShopifyResource
from .productvariant import ProductVariant


class Product(ShopifyResource):
    id: int
    title: str

    def get_variants(self) -> AsyncGenerator[ProductVariant, None]:
        return self._client.listall(ProductVariant, self.id)


    class Meta:
        base_endpoint: str = '/2023-01/products'