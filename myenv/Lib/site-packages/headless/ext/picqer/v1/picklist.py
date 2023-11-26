# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime

from .picklistproduct import PicklistProduct
from .picqerresource import PicqerResource
from .pickliststatus import PicklistStatus


class Picklist(PicqerResource):
    idpicklist: int
    picklistid: str
    idcustomer: int | None
    idorder: int | None
    idreturn: int | None
    idwarehouse: int
    idtemplate: int
    idshippingprovider_profile: int | None
    deliveryname: str | None
    deliverycontactname: str | None
    deliveryaddress: str | None
    deliveryaddress2: str | None
    deliveryzipcode: str | None
    deliverycity: str | None
    deliveryregion: str | None
    deliverycountry: str | None
    telephone: str | None
    emailaddress: str | None
    reference: str | None
    assigned_to_iduser: int | None
    invoiced: bool
    urgent: bool
    preferred_delivery_date: datetime.date | None
    status: PicklistStatus
    totalproducts: int
    totalpicked: int
    snoozed_until: datetime.datetime | None
    closed_by_iduser: int | None
    closed_at: datetime.datetime | None
    created: datetime.datetime
    updated: datetime.datetime | None
    idfulfilment_customer: int | None
    products: list[PicklistProduct] = []

    def is_open(self) -> bool:
        return self.status not in {
            PicklistStatus.cancelled,
            PicklistStatus.cancelled,
            PicklistStatus.snoozed
        }

    class Meta:
        base_endpoint: str = '/v1/picklists'