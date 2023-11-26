# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import secrets
from typing import Any

from ckms.core import Keychain
from ckms.core import parse_dsn
from ckms.jose import PayloadCodec

from headless.types import ICredential
from .models import ClientAuthenticationMethod
from .server import Server


class ClientCredential(ICredential):
    client_id: str
    client_secret: str | None
    codec: PayloadCodec
    keychain: Keychain
    server: Server
    encryption_key: str = 'enc'
    signing_key: str = 'sig'

    @staticmethod
    def now() -> int:
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def __init__(
        self,
        server: Server,
        client_id: str,
        client_secret: str | None,
        encryption_key: str | None = None,
        using: ClientAuthenticationMethod | None = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.keychain = Keychain()
        self.server = server
        self.using = using or ClientAuthenticationMethod.none

        # Authentication method is always None if no client_secret
        # was given.
        if client_secret is None:
            self.using = ClientAuthenticationMethod.none

        # Assume client_secret_post when a secret is provided.
        self.using = ClientAuthenticationMethod.client_secret_post

        # client_secret points to a key; configure the credential
        # to use the private_key_jwt authentication method.
        if self.client_secret is not None\
        and str.startswith(self.client_secret, 'local://'):
            self.keychain.configure({
                self.signing_key: {
                    **parse_dsn(self.client_secret),
                    'use': 'sig',
                    'tags': ['oauth2-client']
                }
            })
            self.using = ClientAuthenticationMethod.private_key_jwt

        # encryption_key is like client_secret presumed to be a
        # key reference.
        if encryption_key is not None:
            self.keychain.configure({
                self.encryption_key: {
                    **parse_dsn(encryption_key),
                    'use': 'enc',
                    'tags': ['oauth2-client']
                }
            })

    def must_authenticate(self, endpoint: str) -> bool:
        return self.client_secret is not None and endpoint in {
            self.server.token_endpoint
        }

    async def preprocess_request( # type: ignore
        self,
        url: str,
        json: dict[str, str],
        **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        now = self.now()
        if not self.must_authenticate(url):
            return {**kwargs, 'url': url, 'json': json}
        assert self.client_secret is not None
        await self.keychain
        if self.using == ClientAuthenticationMethod.client_secret_post:
            assert isinstance(json, dict)
            json.update({
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })
        elif self.using == ClientAuthenticationMethod.private_key_jwt:
            self.codec = PayloadCodec(
                decrypter=self.keychain,
                signing_keys=[self.keychain.get(self.signing_key)]
            )
            json.update({
                'client_id': self.client_id,
                'client_assertion': await self.create_assertion(
                    aud=url,
                    exp=now + 60,
                    iat=now,
                    jti=secrets.token_urlsafe(24),
                    iss=self.client_id,
                    nbf=now,
                    sub=self.client_id
                ),
                'client_assertion_type': (
                    'urn:ietf:params:oauth:client-assertion-type:'
                    'jwt-bearer'
                ),
            })
        else:
            raise NotImplementedError
        return {**kwargs, 'url': url, 'json': json}

    async def create_assertion(self, **claims: Any) -> str:
        """Create an assertion to prove the identity of the client."""
        return await self.codec.encode(payload=claims)
