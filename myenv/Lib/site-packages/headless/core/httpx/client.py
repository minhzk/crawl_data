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

import httpx

from headless.types import IClient
from headless.types import ICredential
from headless.types import IRequest
from headless.types import RequestContent
from ..resource import Resource # type: ignore
from .request import Request
from .response import Response


R = TypeVar('R', bound=Resource)
T = TypeVar('T', bound='Client')


class Client(IClient[httpx.Request, httpx.Response]):
    _client: httpx.AsyncClient
    response_class: type[Response] = Response
    request_class: type[Request] = Request

    @property
    def cookies(self) -> Any:
        return self._client.cookies

    def __init__(self, *, base_url: str, credential: ICredential | None = None, **kwargs: Any):
        self.base_url = base_url
        self.credential = credential or self.credential
        self.params = kwargs
        self._client = httpx.AsyncClient(base_url=base_url, **kwargs)
        self._in_context = False

    def in_context(self) -> bool:
        return self._in_context

    async def request_factory(
        self,
        method: str,
        url: str,
        json: list[Any] | dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        content: RequestContent | None = None
    ) -> httpx.Request:
        return self._client.build_request(
            method=method,
            url=url,
            json=json,
            headers=headers,
            params=params,
            cookies=cookies,
            content=content
        )

    async def send(self, request: IRequest[Any]) -> Response: # type: ignore
        return Response.fromimpl(request, await self._client.send(request.impl))

    async def __aenter__(self: T) -> T:
        if not self.in_context():
            await self._client.__aenter__()
            self._in_context = True
        return self

    async def __aexit__(self, cls: type[BaseException] | None, *args: Any) -> bool | None:
        if self.in_context():
            self._in_context = False
            await self._client.__aexit__(cls, *args)