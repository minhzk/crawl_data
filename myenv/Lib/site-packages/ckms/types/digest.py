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
"""Declares :class:`Digest`."""
import hashlib
from typing import Any

from .data import Data


class Digest(Data):
    """A :class:`~ckms.core.types.Data` implementation that represents a
    digest.
    """
    __module__: str = 'ckms.types'
    digest_oid: dict[str, str] = {
        '1.3.14.3.2.26'         : 'sha1',
        '2.16.840.1.101.3.4.2.1': 'sha256',
        '2.16.840.1.101.3.4.2.2': 'sha384',
        '2.16.840.1.101.3.4.2.3': 'sha512',
    }
    digest_size: dict[str, int] = {
        'sha256': 32,
        'sha384': 48,
        'sha512': 64,
        'sha3_256': 32,
        'sha3_384': 48,
        'sha3_512': 64,
    }

    @staticmethod
    def hasher(oid: str) -> Any:
        return hashlib.new(Digest.digest_oid[oid])

    @classmethod
    def frombytes(cls, algorithm: str, buf: bytes) -> 'Digest':
        hasher = cls.hashers[algorithm]()
        hasher.update(buf)
        return cls(buf=hasher.digest(), digest=algorithm)

    @classmethod
    def fromoid(cls, data: bytes, oid: str) -> 'Digest':
        """Return a new :class:`Digest` configured by OID."""
        return cls.frombytes(algorithm=cls.digest_oid[oid], buf=data)

    def __init__(self, *, buf: bytes, digest: str, **kwargs: Any):
        if digest not in self.hashers:
            raise ValueError(f'Unknown digest algorithm: {digest}.')
        if len(buf) != self.digest_size[digest]:
            raise ValueError(f'Invalid digest length for {digest}.')
        super().__init__(buf=buf, digest=digest, **kwargs)

    async def digest(
        self,
        algorithm: str | None = None,
        length: int | None = None,
        encoding: str | None = None
    ) -> bytes:
        if algorithm is not None and algorithm != self._algorithm:
            raise ValueError("Requested algorithm differs from digest algorithm.")

        # No async call here since the data is already in memory.
        return self.encode(bytes(self), encoding=encoding)