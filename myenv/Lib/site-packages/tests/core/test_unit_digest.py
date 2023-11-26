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
from typing import Any

import pytest

from ckms.types import Digest


ALGORITHMS = [
    'sha256',
    'sha384',
    'sha512',
    'sha3_256',
    'sha3_384',
    'sha3_512'
]

HASHERS = [
    hashlib.sha256,
    hashlib.sha384,
    hashlib.sha512,
    hashlib.sha3_256,
    hashlib.sha3_384,
    hashlib.sha3_512,
]


class TestData:
    impl: type[Digest] = Digest

    @pytest.mark.parametrize("algorithm,factory", zip(ALGORITHMS, HASHERS))
    async def test_bytes(self, algorithm: str, factory: Any):
        digest = await self.impl.frombytes(algorithm, b'Hello world!')
        assert bytes(digest) == factory(b'Hello world!').digest()

    @pytest.mark.parametrize("algorithm,factory", zip(ALGORITHMS, HASHERS))
    async def test_digest(self, algorithm: str, factory: Any):
        digest = await self.impl.frombytes(algorithm, b'Hello world!')
        assert await digest.digest() == factory(b'Hello world!').digest()

    def test_digest_must_be_valid(self):
        with pytest.raises(ValueError):
            Digest(buf=b'foo', digest='foo')

    @pytest.mark.parametrize("algorithm,length", Digest.digest_size.items())
    def test_digest_must_be_valid_length(self, algorithm: str, length: int):
        with pytest.raises(ValueError):
            Digest(buf=b'0' * (length+1), digest=algorithm)

    @pytest.mark.asyncio
    async def test_mismatching_algorithm_raises_valueerror(self):
        digest = await self.impl.frombytes('sha256', b'Hello world!')
        with pytest.raises(ValueError):
            await digest.digest(algorithm='sha384')
