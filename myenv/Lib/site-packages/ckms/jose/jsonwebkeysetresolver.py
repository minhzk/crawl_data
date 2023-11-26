# Copyright 2018 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from httpx import AsyncClient

from ckms.types import JSONWebToken
from ckms.types import JSONWebKeySet
from ckms.types import ServerMetadata
from ckms.types import UntrustedIssuer
from unimatrix.exceptions import CanonicalException
from .joseheaderset import JOSEHeaderSet


class JSONWebKeySetResolver:
    __module__: str = 'ckms.jose'
    issuers: set[str]
    logger: logging.Logger = logging.getLogger()

    def __init__(
        self,
        issuers: str | set[str]
    ):
        if isinstance(issuers, str):
            issuers = {issuers}
        self.issuers = issuers

    async def resolve(
        self,
        jwt: JSONWebToken,
        headers: JOSEHeaderSet | None = None
    ) -> JSONWebKeySet:
        """Resolve keys to verify a JSON Web Token (JWT)"""
        if jwt.iss is None or jwt.iss not in self.issuers:
            raise UntrustedIssuer
        jwks = None
        self.logger.info("Fetching JWKS for issuer %s", jwt.iss)
        async with AsyncClient() as client:
            # Attempt discovery through the OAuth 2.x Metadata Endpoint.
            metadata = await ServerMetadata.discover(
                client=client,
                issuer=jwt.iss
            )
            jwks = await metadata.get_jwks(client)
        if jwks is None:
            self.logger.info("Unable to retrieve JWKS using OAuth 2.0 protocols.")
            raise CanonicalException(
                http_status_code=503,
                code="SERVICE_NOT_AVAILABLE",
                message="The service is currently not available."
            )
        return jwks

