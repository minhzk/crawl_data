# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import date
from datetime import datetime

import pydantic

from .shipmenttrackingnumber import ShipmentTrackingNumber


class ShipmentTrackingInfo(pydantic.BaseModel):
    """Contains information to track the status of a :term:`Shipment` consisting
    of one or multiple packages.
    """
    carrier_id: str = pydantic.Field(
        default=...,
        title="Carrier ID",
        description="An identifier for the the Carrier, usually a domain name."
    )

    carrier_name: str = pydantic.Field(
        default=...,
        title="Carrier",
        description=(
            "The human-readable name of the carrier that is providing the "
            "shipping services."
        )
    )

    trace: ShipmentTrackingNumber | None = pydantic.Field(
        default=None,
        title="Tracking information",
        description=(
            "Tracking information regarding the shipment and its items."
        )
    )

    etd: datetime | date = pydantic.Field(
        default=...,
        title="Estimated Time of Departure (ETD)",
        description=(
            "Expected Time of Departure is the prediction of time "
            "that is expected for a transport system to depart "
            "its point of origin or location. As shipping labels "
            "are usually created prior to actual shipment, this "
            "estimation should be interpreted as *on or before*."
        )
    )
    
    def add(self, trackingcode: str, trackingurl: str | None) -> None:
        if self.trace is not None:
            raise ValueError("ShipmentTrackingInfo.tracking_number is already set.")
        self.trace = ShipmentTrackingNumber(
            number=trackingcode,
            url=trackingurl
        )