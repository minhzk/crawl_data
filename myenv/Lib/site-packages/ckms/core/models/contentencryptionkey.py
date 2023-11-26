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
import inspect
from typing import cast

from ckms.types import CipherText
from ckms.types import IContentEncryptionKey
from ckms.types import IProvider
from ckms.types import PlainText
from ckms.types.encrypter import Encrypter


class ContentEncryptionKey(IContentEncryptionKey):
    __module__: str = 'ckms.core.models'

    @classmethod
    def generate(cls, algorithm: str) -> 'ContentEncryptionKey':
        """Generate a new :class:`ContentEncryptionKey`."""
        provider = IProvider.get('local')
        spec = provider.parse_spec({
            'kty': 'oct',
            'algorithm': algorithm,
        })
        return cls(spec)

    @classmethod
    def null(cls) -> 'ContentEncryptionKey':
        return cls(b'')

    async def encrypt(
        self,
        pt: bytes | PlainText,
        aad: bytes | None = None
    ) -> CipherText:
        """Encrypt the plain text with the CEK."""
        await self
        spec = cast(Encrypter, self.spec)
        ct = await spec.encrypt(pt, aad=aad)
        if inspect.isawaitable(ct):
            ct = await ct
        assert isinstance(ct, CipherText), self.spec
        return ct


    def is_aead(self) -> bool:
        return True