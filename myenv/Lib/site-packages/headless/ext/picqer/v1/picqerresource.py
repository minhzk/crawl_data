# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from headless.core import Resource
from headless.types import IResponse


class PicqerResource(Resource):
    __abstract__: bool = True

    @classmethod
    def get_next_url(
        cls,
        response: IResponse[Any, Any],
        n: int
    ) -> str | None:
        if n == 0:
            raise StopIteration
        offset = int(dict(response.request.params).get('offset') or 0)
        return cls._meta.get_list_url(offset=offset + 100)