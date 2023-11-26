# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .picqerresource import PicqerResource


class Warehouse(PicqerResource):
    idwarehouse: int
    name: str
    accept_orders: bool
    counts_for_general_stock: bool
    priority: int
    active: bool

    class Meta:
        base_endpoint: str = '/v1/warehouses'