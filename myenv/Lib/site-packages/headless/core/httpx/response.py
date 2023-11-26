# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import NoReturn

import httpx
from headless.types import Headers
from headless.types import IResponse


class Response(IResponse[httpx.Request, httpx.Response]):
    __module__: str = 'headless.core.httpx'

    def get_content(self) -> bytes:
        return self._response.content

    def get_headers(self) -> Headers:
        return Headers(dict(self._response.headers.items()))

    def get_status_code(self) -> int:
        return self._response.status_code

    async def json(self) -> Any:
        return self._response.json()

    def raise_for_status(self) -> None | NoReturn:
        self._response.raise_for_status()