# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

import pydantic

from .iresponse import IResponse


T = TypeVar('T', bound='OptionsResponse')


class OptionsResponse(pydantic.BaseModel):
    allowed_http_methods: list[str] = []

    @classmethod
    def parse_response(
        cls: type[T],
        response: IResponse[Any, Any]
    ) -> T:
        methods = response.headers.get('Allow') or ''
        params: dict[str, Any] = {
            'allowed_http_methods': [
                str.upper(str.strip(x))
                for x in str.split(methods, ',')
                if x
            ]
        }
        return cls.parse_obj(params)

    def allows(self, method: str) -> bool:
        return method in self.allowed_http_methods