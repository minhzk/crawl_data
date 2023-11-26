# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from typing import Any

from headless.core import Resource
from headless.types import IResponse


class ShopifyResource(Resource):
    __abstract__: bool = True

    @classmethod
    def get_list_url(cls, *params: Any) -> str:
        url = super().get_list_url(*params) + '.json'
        if params:
            url = url.format(*params)
        return url

    @classmethod
    def get_next_url(
        cls,
        response: IResponse[Any, Any],
        n: int
    ) -> str | None:
        m = re.match('^<([^>]+)>; rel="next"', response.headers.get('link') or '')
        url = None
        if m is not None:
            url = m.group(1)
        return url

    @classmethod
    def process_response(
        cls,
        action: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        if action in {'list'}:
            k = cls._meta.pluralname
        elif action in {'retrieve'}:
            k = cls._meta.name
        elif action is None:
            return data
        else:
            raise NotImplementedError
        return data[str.lower(k)]