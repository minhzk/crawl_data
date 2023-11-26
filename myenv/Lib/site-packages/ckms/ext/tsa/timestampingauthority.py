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
# type: ignore
import inspect
import secrets
from typing import cast
from typing import Any

from cryptography import x509
from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder
from pyasn1_modules import rfc3161

from ckms.types import Digest
from ckms.types import Message
from ckms.types import IHTTPClient
from .types import AlgorithmIdentifier
from .types import Timestamp
from .types import TimeStampResp


class TimestampingAuthority:
    """Provides an interface to create a timestamp using a specific authority."""
    __module__: str = 'ckms.ext.tsa'
    certificate: x509.Certificate | None = None
    digest: str
    url: str

    def __init__(
        self,
        *,
        url: str,
        crtpath: str | None = None,
        digest: str = 'sha1'
    ):
        if crtpath:
            self.certificate = x509.load_pem_x509_certificate(open(crtpath, 'rb').read())
        self.digest = digest
        self.url = url

    def create_request(self, data: bytes, digest_name: str) -> rfc3161.TimeStampReq:
        """Return a byte-sequence containing a DER-encoded :rfc:`3161`
        ``TimeStampReq`` object.
        """
        message = rfc3161.MessageImprint()
        message.setComponentByPosition(0, AlgorithmIdentifier.new(digest_name))
        message.setComponentByPosition(1, data)
        request = rfc3161.TimeStampReq()
        request.setComponentByPosition(0, 'v1')
        request.setComponentByPosition(1, message)
        request.setComponentByPosition(3, self.nonce())
        request.setComponentByPosition(4)
        #with open('request-data.tsq', 'wb') as f: f.write(data)
        return request

    def nonce(self) -> int:
        return int.from_bytes(secrets.token_bytes(64), 'big')

    async def timestamp(
        self,
        *,
        client: Any,
        data: bytes | Digest | Message,
        digest: str | None = None
    ) -> TimeStampResp:
        """Create a timestamp of the given input data."""
        client = cast(IHTTPClient, client)
        if not isinstance(data, (Digest, Message)):
            data = Message(buf=data, digest=digest or self.digest)
        assert isinstance(data, Message)
        request = self.create_request(
            data=await data.digest(),
            digest_name=data.digestmod
        )
        response = client.post(
            url=self.url,
            content=encoder.encode(request),
            headers={
                'Content-Type': 'application/timestamp-query'
            }
        )
        if inspect.isawaitable(response):
            response = await response
        obj, _ = decoder.decode(response.content, asn1Spec=rfc3161.TimeStampResp())
        if _:
            raise ValueError("Invalid response from TSA.")
        #with open('response.tsq', 'wb') as f: f.write(response.content)
        return TimeStampResp.parse_obj({
            **obj,
            'content': response.content,
            'request': request
        })