# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import binascii
import functools
import logging
import urllib.parse
from typing import Any
from typing import NoReturn

from ckms.jose import PayloadCodec
from ckms.types import JSONWebKeySet
from ckms.types import JSONWebToken
from ckms.types import Malformed
from ckms.types import InvalidSignature
from ckms.types.invalidtoken import InvalidToken

from headless.core import httpx
from headless.types import IResponse
from .clientcredential import ClientCredential
from .models import AuthorizationCode
from .models import ClaimSet
from .models import ClientAuthenticationMethod
from .models import ClientCredentialsRequest
from .models import Error
from .models import IObtainable
from .models import OIDCToken
from .models import TokenResponse
from .models import ServerMetadata
from .nullcredential import NullCredential
from .server import Server


class Client(httpx.Client):
    """A :class:`headless.core.httpx.Client` implementation for use with
    Open Authorization/OpenID Connect servers.
    """
    __module__: str = 'headless.ext.oauth2'
    credential: ClientCredential
    jwks: JSONWebKeySet | None = None
    logger: logging.Logger = logging.getLogger('headless.ext.oauth2')
    scope: set[str]
    trust_email: bool

    @property
    def client_id(self) -> str:
        return self.credential.client_id

    @property
    def metadata(self) -> ServerMetadata:
        assert self.server.metadata is not None
        return self.server.metadata

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        issuer: str | None = None,
        client_auth: ClientAuthenticationMethod | None = None,
        authorization_endpoint: str | None = None,
        token_endpoint: str | None = None,
        trust_email: bool = False,
        scope: set[str] | None = None,
        **kwargs: Any
    ):
        self.server = Server(
            client=self,
            autodiscover=bool(issuer),
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            **kwargs
        )
        self.scope = set(scope or set())
        self.trust_email = trust_email

        # If the client_id is None, then this client is configured for
        # a limited set of operations such as discovery, userinfo, etc.
        if client_id is None:
            credential = NullCredential()
        else:
            credential=ClientCredential(
                server=self.server,
                client_id=client_id,
                client_secret=client_secret,
                using=client_auth
            )
        super().__init__(base_url=issuer or '', credential=credential)

    async def authorize(
        self,
        state: str,
        redirect_uri: str | None,
        scope: set[str] | None = None,
        nonce: str | None = None,
        **extra: Any
    ) -> str:
        """Create an authorization request and return the URI to which
        the resource owner must be redirected.

        The `state` parameter is mandatory and is used to correlate the
        redirect to a specific authorization request.

        The `redirect_uri` parameter *might* be optional depending on the
        OAuth 2.x server. If the server does not allow omitting the
        `redirect_uri` parameter, this argument is mandatory.
        """
        scope = set(scope or self.scope)
        if nonce is not None:
            scope.update({'openid', 'profile', 'email'})
            extra.update({'nonce': nonce})
        url=self.server.authorization_endpoint
        params: dict[str, str] = {
            **extra,
            'client_id': self.credential.client_id,
            'state': state,
            'response_type': 'code',
        }
        if redirect_uri is not None:
            params['redirect_uri'] = redirect_uri
        if scope:
            params['scope'] = str.join(' ', sorted(scope))

        # We encode the URL because some libraries use plus
        # encoding.

        # We encode the URL because some libraries use plus
        # encoding.
        url += '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return url


    async def client_credentials(
        self,
        scope: set[str] | str
    ) -> TokenResponse:
        """Obtain an access token using the configured client."""
        if not isinstance(scope, str):
            scope = str.join(' ', sorted(scope))
        return await self.token(ClientCredentialsRequest(scope=scope))

    async def discover(self) -> None:
        await self.server.discover()

    @functools.singledispatchmethod
    async def token(
        self,
        obj: Any,
        **kwargs: Any
    ) -> TokenResponse:
        """Obtain an access token using the given grant."""
        if not isinstance(obj, IObtainable) or self.server.metadata is None:
            raise NotImplementedError
        return await obj.obtain(self, self.server.metadata)

    @token.register
    async def exchange_authorization_code(
        self,
        dto: AuthorizationCode,
        redirect_uri: str
    ) -> TokenResponse:
        params: dict[str, str] = {
            'client_id': self.credential.client_id,
            'code': dto.code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        response = await self.post(
            url=self.server.token_endpoint,
            json=params
        )
        response.raise_for_status()
        return TokenResponse.parse_obj(await response.json())

    async def on_authorize_endpoint_error(
        self,
        response: IResponse[Any, Any]
    ) -> NoReturn:
        response.raise_for_status()
        raise NotImplementedError

    async def on_client_error(
        self,
        response: IResponse[Any, Any]
    ) -> NoReturn | IResponse[Any, Any]:
        try:
            raise Error(**(await response.json()))
        except TypeError:
            pass
        return await super().on_client_error(response)

    async def userinfo(self, token: str) -> ClaimSet:
        """Query the OpenID Connect UserInfo endpoint at the authorization
        server using the given `token`.
        """
        if not self.server.userinfo_endpoint:
            raise NotImplementedError(
                f'Authorization server does not expose the '
                'UserInfo endpoint'
            )
        response = await self.get(url=self.server.userinfo_endpoint)
        return ClaimSet.parse_obj(await response.json())

    async def verify_response(
        self,
        response: TokenResponse
    ) -> None:
        """Verifies the response from the authorization servers' token
        endpoint.
        """
        pass

    async def verify_oidc(
        self,
        token :str,
        nonce: str | None = None,
        audience: set[str] | None = None,
        accept: set[str] | None = None,
        verify_azp: bool = True,
    ) -> bool:
        """Return a boolean indicating if the token could be verified to
        originate from the configured authorization server.
        """
        assert self.server.metadata is not None # nosec
        is_valid = await self.verify(token, nonce=nonce, audience=audience, accept=accept)
        jwt = OIDCToken.parse_jwt(token)
        return is_valid and all([
            jwt.iss == self.server.metadata.issuer,
            jwt.nonce == nonce,
            jwt.azp == self.client_id
        ])

    async def verify(
        self,
        token :str,
        nonce: str | None = None,
        audience: set[str] | None = None,
        accept: set[str] | None = None
    ) -> bool:
        """Return a boolean indicating if the token could be verified to
        originate from the configured authorization server.
        """
        assert self.metadata is not None
        accept = accept or {"at+jwt", "jwt"}
        keychain = None
        if self.credential.keychain:
            await self.credential.keychain
            keychain = self.credential.keychain
        if self.jwks is None:
            self.jwks = JSONWebKeySet()
            if self.metadata.jwks_uri is not None:
                response = await self.get(
                    url=self.metadata.jwks_uri
                )
                if response.status_code != 200:
                    self.logger.critical(
                        "Caught %s response while fetching the server "
                        "JSON Web Keyset. %s.verify() will always return "
                        "False.",
                        response.status_code, type(self).__name__
                    )
                else:
                    self.jwks = JSONWebKeySet.parse_obj(await response.json())
        codec = PayloadCodec(
            decrypter=keychain,
            verifier=self.jwks
        )
        try:
            jwt = await codec.decode(token=token, accept=accept)
            if not isinstance(jwt, JSONWebToken):
                raise TypeError
            jwt.verify(
                issuer=self.metadata.issuer
            )
        except (binascii.Error, Malformed, InvalidSignature, InvalidToken, TypeError):
            return False

        return True

    async def __aenter__(self):
        await super().__aenter__()
        await self.discover()
        return self