# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class PicklistProduct(pydantic.BaseModel):
    idproduct: int
    idorder_product: int | None
    idreturn_product_replacement: int | None
    idvatgroup: int | None = None
    productcode: str
    name: str
    remarks: str | None
    amount: int
    amount_picked: int
    price: float
    weight: int
    stock_location: str | None = None