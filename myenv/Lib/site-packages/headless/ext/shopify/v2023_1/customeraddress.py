# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class CustomerAddress(pydantic.BaseModel):
    address1: str
    address2: str | None
    city: str
    company: str | None
    country: str
    country_code: str
    first_name: str
    last_name: str
    latitude: float | None
    longitude: float | None
    name: str
    phone: str | None
    province: str | None
    province_code: str | None
    zip: str | None