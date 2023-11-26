# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime

from .orderfield import OrderField
from .orderproduct import OrderProduct
from .pickuppointdata import PickupPointData
from .picklist import Picklist
from .picqerresource import PicqerResource
from .tag import Tag


class Order(PicqerResource):
    idorder: int
    idcustomer: int | None = None
    idtemplate: int | None = None
    idshippingprovider_profile: int | None = None
    orderid: str
    deliveryname: str | None = None
    deliverycontactname: str | None = None
    deliveryaddress: str | None = None
    deliveryaddress2: str | None = None
    deliveryzipcode: str | None = None
    deliverycity: str | None = None
    deliveryregion: str | None = None
    deliverycountry: str | None = None
    full_delivery_address: str | None
    invoicename: str | None = None
    invoicecontactname: str | None = None
    invoiceaddress: str | None = None
    invoiceaddress2: str | None = None
    invoicezipcode: str | None = None
    invoicecity: str | None = None
    invoiceregion: str | None = None
    invoicecountry: str | None = None
    full_invoice_address: str | None
    telephone: str | None = None
    emailaddress: str | None = None
    reference: str | None = None
    customer_remarks: str | None = None
    partialdelivery: bool
    discount: float
    invoiced: bool
    status: str
    idfulfilment_customer: int | None
    warehouses: list[int] = []
    tags: dict[str, Tag] = {}
    pickup_point_data: PickupPointData | None
    preferred_delivery_date: datetime.date | None
    language: str | None
    products: list[OrderProduct]
    pricelists: list[int] = []
    picklists: list[Picklist] = []

    # Not documented in resource
    orderfields: list[OrderField] = []

    class Meta:
        base_endpoint: str = '/v1/orders'