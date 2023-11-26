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
import hashlib
import pathlib
from typing import Any

import pytest

from ckms.types import Data
from ckms.utils import b64decode


FILEPATH: pathlib.Path = pathlib.Path(__file__).parent.joinpath('test.txt')

DATA: bytes = open(FILEPATH, 'rb').read()

INPUTS: list[dict[str, Any]] = [
    {'buf': b'Hello world!'},
    {'src': FILEPATH},
    {'src': str(FILEPATH)}
]

ENCODINGS: list[str] = [
    'base64'
]

HASHING_ALGORITHMS = [
    ('sha256', hashlib.sha256),
    ('sha384', hashlib.sha384),
    ('sha512', hashlib.sha512),
    ('sha3_256', hashlib.sha3_256),
    ('sha3_384', hashlib.sha3_384),
    ('sha3_512', hashlib.sha3_512),
]


class BaseDataTestCase:
    impl: type[Data]

    def get_content(self, content: bytes) -> bytes:
        return content

    def get_digest(self, factory: Any, data: Data) -> bytes:
        return factory(bytes(data)).digest() # type: ignore

    @pytest.mark.parametrize("params", INPUTS)
    @pytest.mark.asyncio
    async def test_iter(self, params: dict[str, Any]):
        data = self.impl(**params)
        async for chunk in data.chunks(length=1):
            assert len(chunk) == 1

    @pytest.mark.parametrize("params", INPUTS)
    @pytest.mark.asyncio
    async def test_iter_content(self, params: dict[str, Any]):
        data = self.impl(**params)
        content = b''
        async for chunk in data.chunks(length=1):
            content += chunk
        assert content == self.get_content(b'Hello world!')

    @pytest.mark.parametrize("hasher", HASHING_ALGORITHMS)
    @pytest.mark.parametrize("params",INPUTS)
    @pytest.mark.asyncio
    async def test_digest(
        self,
        hasher: Any,
        params: dict[str, Any]
    ):
        algorithm, factory = hasher
        data = self.impl(**params)
        digest = await data.digest(algorithm=algorithm)
        hasher = factory(bytes(data))
        assert len(digest) == len(hasher.digest())
        assert digest == self.get_digest(factory, data)

    def test_src_or_buf_is_required(self):
        with pytest.raises(TypeError):
            self.impl()

    def test_src_and_buf_is_exception(self):
        with pytest.raises(TypeError):
            self.impl(src='foo.txt', buf=b'')

    @pytest.mark.parametrize("hasher", HASHING_ALGORITHMS)
    @pytest.mark.parametrize("params",INPUTS)
    @pytest.mark.asyncio
    async def test_algorithm_from_constructor(
        self,
        hasher: Any,
        params: dict[str, Any]
    ):
        algorithm, factory = hasher
        data = self.impl(digest=algorithm, **params)
        assert await data.digest() == self.get_digest(factory, data)

    @pytest.mark.asyncio
    async def test_algorithm_is_required_if_not_in_constructor(self):
        data = self.impl(buf=DATA)
        with pytest.raises(TypeError):
            await data.digest()

    @pytest.mark.parametrize("algorithm", [x[0] for x in HASHING_ALGORITHMS])
    @pytest.mark.parametrize("encoding", ENCODINGS)
    @pytest.mark.parametrize("verify", [b64decode])
    @pytest.mark.parametrize("params", INPUTS)
    @pytest.mark.asyncio
    async def test_encode_digest(
        self,
        algorithm: str,
        encoding: str,
        verify: Any,
        params: dict[str, Any]
    ):
        data = self.impl(**params)
        digest = await data.digest(
            algorithm=algorithm,
            encoding=encoding
        )
        assert verify(digest) == await data.digest(algorithm=algorithm)