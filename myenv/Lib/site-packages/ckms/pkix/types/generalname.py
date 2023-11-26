# Copyright 2022 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any

import pydantic
from typing_extensions import Annotated

from .name import Name
from .dnsname import DNSName
from .uriname import URIName
from .ipaddressname import IPAddressName



class GeneralName(pydantic.BaseModel):
    __root__: Annotated[
        DNSName | IPAddressName | URIName,
        pydantic.Field(discriminator='kind')
    ]

    @classmethod
    def parse_obj(cls, obj: Any) -> Name:
        return super().parse_obj(obj).__root__