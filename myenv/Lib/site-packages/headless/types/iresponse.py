# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import NoReturn
from typing import TypeVar

from .headers import Headers
from .irequest import IRequest


W = TypeVar('W')
Request = TypeVar('Request')
Response = TypeVar('Response')

class IResponse(Generic[Request, Response]):
    """A wrapper for response objects."""
    __module__: str = 'headless.core'
    _request: IRequest[Request]
    _response: Response

    @classmethod
    def fromimpl(
        cls: type[W],
        request: IRequest[Request],
        response: Response
    ) -> W:
        return cls(request, response)

    @property
    def content(self) -> bytes:
        return self.get_content()

    @property
    def headers(self) -> Headers:
        return self.get_headers()

    @property
    def impl(self) -> Response:
        return self._response

    @property
    def request(self) -> IRequest[Request]:
        return self._request

    @property
    def status_code(self) -> int:
        return self.get_status_code()

    def __init__(self, request: IRequest[Request], response: Response) -> None:
        self._request = request
        self._response = response

    def get_content(self) -> bytes:
        raise NotImplementedError

    def get_headers(self) -> Headers:
        raise NotImplementedError

    def get_status_code(self) -> int:
        raise NotImplementedError

    async def json(self) -> Any:
        raise NotImplementedError

    def raise_for_status(self) -> None | NoReturn:
        """Raises an exception according to the HTTP response
        status code, if applicable.
        """
        raise NotImplementedError