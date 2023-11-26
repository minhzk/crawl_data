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
import secrets
from typing import Any
from typing import Generator

from cryptography.hazmat.primitives.ciphers.algorithms import AES

from .decrypter import Decrypter
from .encrypter import Encrypter
from .ikeyspecification import IKeySpecification
from .iprovider import IProvider


class IContentEncryptionKey(Decrypter, Encrypter):
    __module__: str = 'ckms.types'
    algorithms: dict[str, dict[str, int]] = {
        'A128GCM': {'nbytes': 16},
        'A192GCM': {'nbytes': 24},
        'A256GCM': {'nbytes': 32},
        'A128CBC': {'nbytes': 16},
        'A192CBC': {'nbytes': 24},
        'A256CBC': {'nbytes': 32},
    }
    __spec: IKeySpecification

    @property
    def algorithm(self) -> str:
        return self.__spec.algorithm

    @property
    def iv(self) -> bytes:
        return self.__iv

    @property
    def provider(self) -> IProvider:
        return self.__spec.provider

    @property
    def spec(self) -> IKeySpecification:
        return self.__spec

    @classmethod
    def generate(cls, algorithm: str) -> 'IContentEncryptionKey':
        """Generate a new :class:`ContentEncryptionKey`."""
        raise NotImplementedError

    def __init__(self, spec: IKeySpecification):
        self.__spec = spec
        self.__iv = secrets.token_bytes(12)

    def get_private_key(self) -> AES:
        return self.__spec.get_private_key()

    def is_aead(self) -> bool:
        raise NotImplementedError

    def __await__(self) -> Generator[Any, None, 'IContentEncryptionKey']:
        async def f():
            if not self.__spec.is_loaded():
                await self.__spec
            return self
        return f().__await__()

    def __bool__(self) -> bool:
        return bool(self.__spec)

    def __bytes__(self) -> bytes:
        return self.__spec.get_private_bytes()

    def __len__(self) -> int:
        return self.algorithms[self.spec.algorithm]['nbytes'] # type: ignore