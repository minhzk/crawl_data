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
import asyncio
import random
from typing import cast
from typing import Any
from typing import Awaitable

from ckms.types import Digest
from ckms.types import Message
from ckms.types import IHTTPClient
from .timestampingauthority import TimestampingAuthority
from .types import TimeStampResp


class Timestamper:
    """Provides an interface to retrieve a timestamp of a digest
    using multiple :rfc:`3161` timestamping CAs.
    """
    __module__: str = 'ckms.ext.tsa'
    servers: list[TimestampingAuthority]

    @staticmethod
    def default() -> 'Timestamper':
        return _default

    @classmethod
    def fromlist(cls, authorities: list[dict[str, Any]]) -> 'Timestamper':
        return cls(list(TimestampingAuthority(**x) for x in authorities))

    def __init__(self, servers: list[TimestampingAuthority]):
        self.servers = servers

    def select(self, n: int) -> list[TimestampingAuthority]:
        """Select the given number of :class:`TimestampingAuthority`
        instances from the preconfigured list.
        """
        selected: list[TimestampingAuthority] = []
        candidates = list(self.servers)
        while candidates:
            i = random.choice(range(len(candidates)))
            selected.append(candidates.pop(i))
            if len(selected) == n:
                break
        return selected

    async def timestamp(
        self,
        client: Any,
        data: bytes | Digest | Message,
        digestmod: str = 'sha256',
        min_signatures: int = 1,
        retry: int = 0,
    ) -> list[TimeStampResp]:
        """Return a list of :rfc:`3161` timestamps, represented as :class:`Timestamp`
        instances, for the given input data `data` using hashing algorithm `digestmod`.

        The `min_signatures` parameter specifies how many signatures must be
        obtained for the input data. The output is not guaranteed to contain `n`
        signatures; the `min_signatures` parameter solely indicates the number
        of authorities that should be attempted.
        """
        if isinstance(data, Digest) and data.digestmod != digestmod:
            assert data.digestmod is not None
            digestmod = data.digestmod
        client = cast(IHTTPClient, client)
        futures: list[Awaitable[TimeStampResp]] = []
        for tsa in self.select(min_signatures):
            fut = tsa.timestamp(
                client=client,
                data=data,
                digest=digestmod
            )
            futures.append(fut)
        return cast(list[TimeStampResp], await asyncio.gather(*futures))


_default: Timestamper = Timestamper([])