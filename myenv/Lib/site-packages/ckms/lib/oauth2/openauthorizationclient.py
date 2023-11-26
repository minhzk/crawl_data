"""Declares :class:`OpenAuthorizationClient`."""
from curses import meta
import logging
import typing

import httpx
import pydantic

from .servermetadata import ServerMetadata


class OpenAuthorizationClient(httpx.AsyncClient):
    __module__: str = 'ckms.lib.oauth2'
    metadata: typing.Optional[ServerMetadata] = None
    oauth2_metadata_endpoint: str = "/.well-known/oauth-authorization-server"
    openid_configuration: str = "/.well-known/openid-configuration"
    logger: logging.Logger = logging.getLogger('oauth2.client')
    keys: typing.Dict[str, typing.Any]

    def __init__(
        self,
        server: str,
        logger: typing.Optional[logging.Logger] = None,
        **kwargs: typing.Any
    ):
        kwargs['base_url'] = server
        super().__init__(**kwargs) # type: ignore
        self.logger = logger or self.logger
        self.keys = {}
        self.server = server

    async def get_metadata(self) -> ServerMetadata:
        """Return the server metadata as exposed by the OAuth 2.0
        metadata endpoint or OpenID configuration endpoint.
        """
        try:
            metadata = ServerMetadata(**(
                await self.get_openid_configuration()
                or await self.get_authorization_server_metadata()
                or {}
            ))
            if metadata.jwks_uri:
                self.keys = await self.fetch_metadata(metadata.jwks_uri)
            return metadata
        except pydantic.ValidationError:
            self.logger.warning(
                "Invalid OAuth 2.0 metadata sent by %s", self.server
            )
            return ServerMetadata()

    async def get_authorization_server_metadata(
        self
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return await self.fetch_metadata(self.oauth2_metadata_endpoint)

    async def get_openid_configuration(
        self
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        return await self.fetch_metadata(self.openid_configuration)

    async def fetch_metadata(
        self,
        url: str
    ) -> typing.Dict[str, typing.Any]:
        try:
            response = await self.get(url) # type: ignore
            return response.json()
        except (httpx.HTTPError, httpx.StreamError, TypeError, ValueError) as exc:
            self.logger.warning(
                "Caught fatal %s during metadata lookup.",
                type(exc).__name__
            )
            return {}

    async def __aenter__(self):
        await super().__aenter__()
        if self.metadata is None:
            self.metadata = await self.get_metadata()
        return self