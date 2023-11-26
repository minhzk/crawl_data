# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import urllib.parse
from typing import Any

import httpx
from headless.types import IClient
from headless.types import IRequest
from headless.types import ServerDoesNotExist


class Request(IRequest[httpx.Request]):
    __module__: str = 'headless.core.httpx'

    def add_header(self, name: str, value: str) -> None:
        self._request.headers[name] = value

    def get_params(self) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        if self._request.url.query:
            params.extend(urllib.parse.parse_qsl(self._request.url.query.decode()))
        return params

    def get_url(self) -> str:
        return str(self._request.url)

    @functools.singledispatchmethod # type: ignore
    async def on_failure(
        self,
        exc: BaseException,
        client: IClient[Any, Any],
    ) -> Any | None:
        return await super().on_failure(exc, client)

    @on_failure.register
    async def on_connection_error(
        self,
        exc: httpx.ConnectError,
        client: IClient[Any, Any]
    ) -> Any | None:
        if not exc.args:
            return None
        msg = exc.args[0]
        if msg == '[Errno 8] nodename nor servname provided, or not known':
            raise ServerDoesNotExist(self)