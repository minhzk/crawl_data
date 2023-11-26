# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from typing import Any
from typing import Literal
from typing import TypeAlias


class BasePickupPointData(pydantic.BaseModel):
    carrier: str


class B2CEurope(pydantic.BaseModel):
    carrier: Literal['b2ceurope']
    id: str


class DefaultPickupPointData(BasePickupPointData):
    id: str
    name: str
    street: str
    house_number: str
    zipcode: str
    city: str
    country: str
    options: dict[str, Any]


PickupPointData: TypeAlias = B2CEurope | DefaultPickupPointData