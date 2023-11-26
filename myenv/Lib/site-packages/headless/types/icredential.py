# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .iclient import IClient
from .iresponse import IResponse
from .irequest import IRequest


class ICredential:
    """The base class for all HTTP credential implementations."""
    __module__: str = 'headless.types'

    async def add_to_request(self, request: IRequest[Any]) -> None:
        """Modify a :class:`Request` instance to include this
        credential.
        """
        pass

    async def preprocess_request(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """Preprocesses the parameters used to build a request."""
        return kwargs

    async def preprocess_json(
        self,
        json: dict[str, Any] | list[Any]
    ) -> dict[str, Any] | list[Any]:
        """Preprocess the JSON payload of a request."""
        return json

    async def send(
        self,
        client: 'IClient[Any, Any]',
        request: IRequest[Any]
    ) -> IResponse[Any, Any]:
        response = await client.send(request)
        return await self.process_response(client, response.request, response)

    async def process_response(
        self,
        client: 'IClient[Any, Any]',
        request: IRequest[Any],
        response: IResponse[Any, Any]
    ) -> IResponse[Any, Any]:
        return response