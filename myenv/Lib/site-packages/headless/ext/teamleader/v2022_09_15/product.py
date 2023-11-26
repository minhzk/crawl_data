# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ..resource import TeamleaderResource
from .productprice import ProductPrice


class Product(TeamleaderResource):
    id: str
    name: str
    description: str
    code: str
    purchase_price: ProductPrice | None = None
    selling_price: ProductPrice | None = None

    class Meta(TeamleaderResource.Meta):
        base_endpoint: str = '/products'