# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generator
from typing import TypeVar

from headless.types import IClient
from .models import ClientAuthenticationMethod
from .models import ServerMetadata


T = TypeVar('T', bound='Server')


class Server:
    """Represents an OAuth 2.0 and provides an interface to
    inspect the server capabilities.
    """
    _metadata: dict[str, ServerMetadata] = {}
    client: IClient[Any, Any]
    url: str
    discovery_urls: list[str] = [
        '/.well-known/oauth-authorization-server',
        '.well-known/openid-configuration'
    ]

    @property
    def authorization_endpoint(self) -> str:
        assert self.metadata is not None
        if self.metadata.authorization_endpoint is None:
            raise NotImplementedError(
                "Server does not implement authorization code flow."
            )
        return self.metadata.authorization_endpoint

    @property
    def metadata(self) -> ServerMetadata | None:
        return Server._metadata.get(self.client.base_url)

    @metadata.setter
    def metadata(self, value: ServerMetadata) -> None:
        Server._metadata[self.client.base_url] = value

    @property
    def token_endpoint(self) -> str | None:
        if self.metadata is not None:
            return self.metadata.token_endpoint

    @property
    def userinfo_endpoint(self) -> str | None:
        if self.metadata is not None:
            return self.metadata.userinfo_endpoint

    def __init__(
        self,
        client: IClient[Any, Any],
        autodiscover: bool = True,
        **params: Any
    ):
        self.client = client
        if params and not autodiscover:
            self.metadata = ServerMetadata.parse_obj(params)

    async def discover(self: T) -> T:
        if self.metadata is None:
            for url in self.discovery_urls:
                response = await self.client.get(url=url, allow_none=True)
                if response.status_code != 200:
                    continue
                self.metadata = ServerMetadata.parse_obj(await response.json())
                break
            else:
                raise ValueError("Unable to discover OAuth 2.x server.")
        return self

    def supports_auth(self, method: ClientAuthenticationMethod) -> bool:
        assert self.metadata is not None
        return method in self.metadata.token_endpoint_auth_methods_supported

    def __await__(self: T) -> Generator[None, None, T]:
        return self.discover().__await__()