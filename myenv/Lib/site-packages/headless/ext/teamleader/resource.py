# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from headless.core import Resource


T = TypeVar('T', bound='TeamleaderResource')


class TeamleaderResource(Resource):
    __abstract__: bool = True

    @classmethod
    def get_list_url(cls, *params: Any) -> str:
        return f'{cls._meta.base_endpoint}.list'

    @classmethod
    def get_retrieve_url(cls: type[T], resource_id: int | str | None) -> str:
        return f'{cls._meta.base_endpoint}.info'

    @classmethod
    def process_response(
        cls,
        action: str | None,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        if action is None:
            return data
        if action in {'retrieve', 'list'}:
            k = 'data'
        else:
            raise NotImplementedError
        return data[k]

    class Meta:
        headers: dict[str, str] = {
            'X-Api-Version': '2022-09-15'
        }