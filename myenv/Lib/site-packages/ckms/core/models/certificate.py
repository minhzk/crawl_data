# Copyright 2022 Cochise Ruhulessin
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
import base64
from typing import Any

import httpx
import pydantic
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding

from ckms.utils import b64encode_sha1
from ckms.utils import b64encode_sha256
from ckms.utils import certificate_chain


class Certificate(pydantic.BaseModel):
    uri: str
    _certificates: list[tuple[x509.Certificate, bytes]] = pydantic.PrivateAttr(default=[])

    @property
    def x5c(self) -> list[str]:
        return [
            bytes.decode(base64.b64encode(der))
            for _, der in self._certificates
        ]

    @property
    def x5t(self) -> str:
        return bytes.decode(b64encode_sha1(self._certificates[0][1]))

    @property
    def x5t_sha256(self) -> str:
        return bytes.decode(b64encode_sha256(self._certificates[0][1]))

    @property
    def x5u(self) -> str:
        return self.uri

    def claims(self) -> dict[str, Any]:
        return {
            'x5u': self.uri,
            'x5t': self.x5t,
            'x5t#S256': self.x5t_sha256,
            'x5c': self.x5c
        }

    async def load(self) -> None:
        """Fetch the certificate from :attr:`uri`. The content is
        expected to be a PEM-encoded X.509 certificates. Additional
        certificates are the chain.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url=self.uri) # type: ignore
            for pem in certificate_chain(response.content):
                crt = x509.load_pem_x509_certificate(pem)
                self._certificates.append(
                    (crt, crt.public_bytes(Encoding.DER))
                )

    class Config:
        arbitrary_types_allowed: bool = True