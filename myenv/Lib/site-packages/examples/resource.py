# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import enum

import canonical
import pydantic
from canonical.resource import Resource


class OrderState(str, enum.Enum):
    placed = 'placed'
    failed = 'failed'
    accepted = 'accepted'
    rejected = 'rejecred'


class FulfillmentStatus(str, enum.Enum):
    observe = 'observe'
    pending = 'pending'
    shipped = 'shipped'


class OrderLineStatus(pydantic.BaseModel):
    line_id: int | None = pydantic.Field(..., alias='lineId')

    fulfillment: FulfillmentStatus

    product_id: int = pydantic.Field(
        default=...,
        alias='productId'
    )

    external_id: int = pydantic.Field(
        default=0,
        alias='externalId'
    )

    class Config:
        allow_population_by_field_name: bool = True


class OrderStatus(pydantic.BaseModel):
    order_id: int | None = pydantic.Field(None, alias='orderId')

    state: OrderState = pydantic.Field(
        default=OrderState.placed,
        title='State',
        description=(
            "Contains the current state of the `Order` resource."
        )
    )

    reason: str | None = pydantic.Field(
        default=None,
        title='Reason',
        description="Explains why the order is in the current state."
    )

    items: list[OrderLineStatus] = []


class OrderLine(pydantic.BaseModel):
    external_product_id: int = pydantic.Field(
        default=...,
        alias='externalProductId'
    )
    sku: str
    amount: int
    external_id: int = pydantic.Field(
        default=0,
        alias='externalId'
    )

    class Config:
        allow_population_by_field_name: bool = True


class ExternalOrderStatus(pydantic.BaseModel):
    pass


class ExternalOrderSpec(pydantic.BaseModel):
    account: str
    service: str
    external_order_id: int = pydantic.Field(
        default=...,
        alias='externalOrder'
    )

    billing_address: canonical.GenericPostalAddress = pydantic.Field(
        default=...,
        alias='billingAddress',
        title='Billing address',
    )

    placed: datetime.datetime = pydantic.Field(
        default=...,
        title='Placed',
        description=(
            "The date/time at which the order was placed in the external "
            "system."
        )
    )

    shipping_address: canonical.GenericPostalAddress | None = pydantic.Field(
        default=None,
        alias='shippingAddress'
    )
    store: str
    items: list[OrderLine] = []

    class Config:
        allow_population_by_field_name: bool = True


class ExternalOrder(Resource, group='uplink.molano.nl', version='v1'):
    spec: ExternalOrderSpec
    status: OrderStatus = pydantic.Field(
        default_factory=OrderStatus
    )

    def generate_name(self) -> str:
        return f'{self.spec.store}/orders/{self.spec.external_order_id}'

    class Config:
        annotations: bool = True
        labels: bool = True


meta = {
    'name': 'molano-uplink.myshopify.com/orders/1',
    'labels': {
        'uplink.molano.nl/platform': 'shopify'
    }
}
spec = {
    'account': 'molano',
    'service': 'molano-uplink',
    'externalOrder': 1,
    'placed': datetime.datetime.utcnow(),
    'store': 'molano-uplink.myshopify.com',
    'billingAddress': {
        'addressee': "Molano B.V.",
        'contact_name': 'Laili Ishaqzai',
        'address1': "Tappersweg 8N",
        'postal_code': '2031ET',
        'city': 'Haarlem',
        'country': 'NL'
    },
    'shippingAddress': {
        'addressee': 'Wizards of Industry Holding B.V.',
        'contact_name': "Cochise Ruhulessin",
        'address1': "Koningin Julianaplein 10",
        'postal_code': "2595AA",
        'city': 'Den Haag',
        'country': 'NL'
    },
    'items': [
        {
            'external_product_id': 1,
            'amount': 2,
            'sku': 'XXXTEST',
            'external_id': 5
        },
        {
            'external_product_id': 1,
            'amount': 2,
            'sku': 'XXXBAR'
        },
    ]
}

dto = ExternalOrder.restore(
    uid=124,
    name='molano-uplink.myshopify.com/orders/1',
    created=datetime.datetime.utcnow(),
    spec=spec,
    metadata=meta
)

#print(dto.json(by_alias=True, exclude_none=True, indent=2))

dto2 = ExternalOrder.new(None, spec)
dto2.annotate('must-refresh', True)
dto2.label('uplink.molano.nl/platform','shopify')
dto2.set_status({
    'items': [
        {
            'line_id': 86868,
            'product_id': 124,
            'fulfillment': FulfillmentStatus.observe,
            'external_id': 5
        },
    ]
})
print(dto2.json(by_alias=True, indent=2))
print(ExternalOrder.Config.pluralname)
