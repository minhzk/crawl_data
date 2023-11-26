# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from base64 import b64encode
from typing import Any

from .icredential import ICredential
from .irequest import IRequest


class BasicAuth(ICredential):
    """
    Allows the 'auth' argument to be passed as a (username, password) pair,
    and uses HTTP Basic authentication.
    """
    __module__: str = 'headless.types'

    @staticmethod
    def to_bytes(value: str | bytes, encoding: str = "utf-8") -> bytes:
        return value.encode(encoding) if isinstance(value, str) else value

    def __init__(
        self,
        username: str | bytes,
        password: str | bytes
    ):
        self._auth_header = self._build_auth_header(username, password)

    async def add_to_request(self, request: IRequest[Any]) -> None:
        request.add_header('Authorization', self._auth_header)

    def _build_auth_header(
        self,
        username: str | bytes,
        password: str | bytes
    ) -> str:
        userpass = b":".join((self.to_bytes(username), self.to_bytes(password)))
        token = b64encode(userpass).decode()
        return f"Basic {token}"