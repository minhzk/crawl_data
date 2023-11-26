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
"""Declares :class:`Data`."""
import hashlib
import io
import pathlib
from typing import Any
from typing import AsyncGenerator
from typing import Callable
from typing import Generator
from typing import TypeAlias

import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper
from aiofiles.threadpool.binary import AsyncBufferedReader

from ..utils import b64encode
from .ihasher import IHasher


File: TypeAlias = AsyncBufferedReader | AsyncTextIOWrapper


class Data:
    """A base class for objects on which a cryptographic operation may
    be performed, such as signing or encryption.
    """
    __module__: str = 'ckms.types'
    _buf: bytes | None
    _algorithm: str | None
    _src: pathlib.Path | None
    content_type: str | None
    encoders: dict[str, Callable[..., bytes]] = {
        'base64': b64encode
    }
    hashers: dict[str, Callable[..., IHasher]] = { # type: ignore
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512,
    }
    readlen: int

    @property
    def digestmod(self) -> str | None:
        return self._algorithm

    def __init__(
        self,
        buf: bytes | None = None,
        src: str | pathlib.Path | None = None,
        readlen: int = 1048,
        digest: str | None = None,
        content_type: str | None = None
    ):
        self._algorithm = digest
        if not ((buf is not None) ^ (src is not None)):
            raise TypeError("Provide either the `buf` or `src` parameter.")
        self._buf = buf
        if src is not None and not isinstance(src, pathlib.Path):
            src = pathlib.Path(src)
        self._src = src
        self.content_type = content_type
        self.readlen = readlen

    def base64(self) -> bytes:
        return b64encode(bytes(self))

    async def as_bytes(self) -> bytes:
        if self._buf is None:
            self._buf = b''
            async for chunk in self.chunks():
                self._buf += chunk
        return self._buf

    async def digest(
        self,
        algorithm: str | None = None,
        length: int | None = None,
        encoding: str | None = None
    ) -> bytes:
        """Return a digest of the data using the given digest algorithm."""
        algorithm = algorithm or self._algorithm
        if algorithm is None:
            raise TypeError("The `algorithm` parameter can not be None.")
        hasher = self.hashers[algorithm]()
        async for chunk in self.chunks(length=length):
            hasher.update(chunk)
        return self.encode(hasher.digest(), encoding=encoding)

    async def _read(self) -> 'Data':
        await self.as_bytes()
        return self

    def encode(self, data: bytes, encoding: str | None) -> bytes:
        """Encode the data in the given encoding."""
        if encoding is not None:
            data = self.encoders[encoding](data)
        return data

    async def chunks(self, length: int | None = None) -> AsyncGenerator[bytes, None]:
        length = length or self.readlen
        if self._buf is not None:
            buf = io.BytesIO(self._buf)
            chunk = buf.read(length)
            while chunk:
                yield chunk
                chunk = buf.read(length)
            return
        async with aiofiles.open(self._src, 'rb') as f: # type: ignore
            self._buf = b''
            chunk = await f.read(length) # type: ignore
            while chunk:
                self._buf += chunk
                yield chunk
                chunk = await f.read(length) # type: ignore

    def set_digest_algorithm(self, algorithm: str) -> None:
        self._algorithm = algorithm

    def __bytes__(self) -> bytes:
        if self._buf is not None: return self._buf
        with open(self._src, 'rb') as f: # type: ignore
            return f.read() # type: ignore

    def __await__(self) -> Generator[Any, None, 'Data']:
        return self._read().__await__()