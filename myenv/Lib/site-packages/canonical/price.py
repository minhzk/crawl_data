# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import decimal

import pydantic


class Price(pydantic.BaseModel):
    currency: str = pydantic.Field(
        default=...,
        title="Currency",
        description=(
            "The ISO 4217 currency specifying the monetary unit in which "
            "the price is defined."
        )
    )

    amount: decimal.Decimal = pydantic.Field(
        default=...,
        title="Amount",
        description="Volume of the monetary unit that compose the price."
    )

    class Config:
        json_encoders = {
            decimal.Decimal: str
        }