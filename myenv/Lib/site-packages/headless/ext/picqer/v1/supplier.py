# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .picqerresource import PicqerResource


class Supplier(PicqerResource):
    idsupplier: int
    name: str | None
    address: str | None = None
    address2: str | None = None
    zipcode: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    contactname: str | None
    telephone: str | None
    emailaddress: str | None
    remarks: str | None

    class Meta:
        base_endpoint: str = '/v1/suppliers'