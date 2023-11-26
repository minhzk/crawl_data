# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import decimal
from typing import Any

from ..resource import ShopifyResource
from .clientdetails import ClientDetails
from .customer import Customer
from .customeraddress import CustomerAddress
from .orderfinancialstatus import OrderFinancialStatus
from .orderfulfillmentstatus import OrderFulfillmentStatus
from .ordernoteattribute import OrderNoteAttribute
from .orderprocessingmethod import OrderProcessingMethod


class Order(ShopifyResource):
    app_id: int
    billing_address: CustomerAddress | None
    browser_ip: str
    buyer_accepts_marketing: bool
    cancel_reason: str | None
    cancelled_at: datetime.datetime | None
    cart_token: str | None
    checkout_token: str | None
    client_details: ClientDetails
    closed_at: datetime.datetime | None
    company: dict[str, Any] | None
    created_at: datetime.datetime
    currency: str
    current_total_discounts: decimal.Decimal
    #TODO: current_total_discounts_set
    #TODO: current_total_duties_set
    current_total_price: decimal.Decimal
    #TODO: current_total_price_set
    current_subtotal_price: decimal.Decimal
    #TODO: current_subtotal_price_set
    current_total_tax: decimal.Decimal
    #TODO: current_total_tax_set
    customer: Customer | None
    customer_locale: str | None
    #TODO: discount_applications
    #TODO: discount_codes
    email: str | None
    estimated_taxes: bool
    financial_status: OrderFinancialStatus
    #TODO: fulfillments
    fulfillment_status: OrderFulfillmentStatus | None
    gateway: str | None
    id: int
    landing_site: str | None
    #TODO: line_items
    location_id: int | None
    merchant_of_record_app_id: int | None
    name: str
    note: str | None
    note_attributes: list[OrderNoteAttribute]
    number: int
    order_number: int
    #TODO: original_total_duties_set
    order_status_url: str
    #TODO: payment_details
    #TODO: payment_terms
    payment_gateway_names: list[str]
    phone: str | None
    presentment_currency: str
    processed_at: datetime.datetime | None
    processing_method: OrderProcessingMethod
    referring_site: str | None
    #TODO: refunds
    shipping_address: CustomerAddress | None
    #TODO: shipping_lines
    source_name: str
    source_identifier: str
    source_url: str | None

    # This value is documented as a number but is actually a string
    subtotal_price: decimal.Decimal
    tags: str
    #TODO: tax_lines
    taxes_included: bool
    test: bool
    token: str
    total_discounts: decimal.Decimal
    #TODO: total_discounts_set
    total_line_items_price: decimal.Decimal
    #TODO: total_line_items_price_set
    total_outstanding: decimal.Decimal
    total_price: decimal.Decimal
    #TODO: total_price_set
    #TODO: total_shipping_price_set
    total_tax: decimal.Decimal
    #TODO: total_tax_set
    total_tip_received: decimal.Decimal
    total_weight: int
    updated_at: datetime.datetime | None
    user_id: int | None

    class Meta:
        base_endpoint: str = '/2023-01/orders'