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
from typing import Any

from ckms.types import CipherText
from ckms.types import Encrypter
from ckms.types import IContentEncryptionKey
from ckms.utils import b64encode_str


class Recipient:
    __module__: str = 'ckms.jose'
    direct: bool
    encrypter: Encrypter
    encryption_key: str
    header: dict[str, Any]

    def __init__(
        self,
        *,
        encrypter: Encrypter,
        header: dict[str, Any] | None = None,
    ):
        if encrypter.kid is None:
            raise ValueError("Encrypter.kid must not be None")
        self.encrypter = encrypter
        self.encryption_key = ''
        self.header = header or {}

    def dict(self, compact: bool = False, flatten: bool = False) -> dict[str, Any]:
        """Return a datastructure describing the recipient."""
        return {
            'encrypted_key': self.encryption_key,
            'header': self.header
        }

    async def encrypt(self, cek: IContentEncryptionKey) -> None:
        """Encrypt the Content Encryption Key (CEK) using the recipient
        key.
        """
        # If cek and self.encrypter are the same, then Direct Encryption or
        # Direct Key Agreement is used.
        is_direct = cek == self.encrypter
        self.header['kid'] = self.encrypter.kid
        if not is_direct:
            await cek
            ct = await self.encrypter.wrap(bytes(cek))
            assert isinstance(ct, CipherText)
            self.header['alg'] = self.encrypter.algorithm
            if ct.iv:
                self.header['iv'] = b64encode_str(ct.iv)
            if ct.tag:
                self.header['tag'] = b64encode_str(ct.tag)
            self.encryption_key = bytes.decode(ct.base64(), 'ascii')
        elif is_direct:
            self.header['alg'] = 'dir'