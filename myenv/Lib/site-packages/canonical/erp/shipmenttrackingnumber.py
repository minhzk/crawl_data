# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class ShipmentTrackingNumber(pydantic.BaseModel):
    number: str = pydantic.Field(
        default=...,
        title="Number",
        description=(
            "An identifier issued by a Carrier to reference "
            "a Shipment."
        )
    )

    url: str | None = pydantic.Field(
        default=None,
        title="URL",
        description=(
            "A URL pointing to a web page where more information regarding the "
            "Shipment may be retrieved."
        )
    )

    def __str__(self) -> str:
        return self.number