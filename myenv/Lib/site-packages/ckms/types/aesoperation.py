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
"""Declares :class:`AESOperation`."""
from typing import Any

from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from .ciphertext import CipherText
from .operation import Operation
from .plaintext import PlainText


class AESOperation(Operation):
    content: CipherText | PlainText # type: ignore
    _aad: bytes | None
    _mode: str
    _padding: str | None

    @property
    def aad(self) -> bytes | None:
        return self._aad

    @property
    def mode(self) -> type[modes.CBC] | type[modes.GCM]:
        assert self._mode in {'CBC', 'GCM'}, self._mode
        return getattr(modes, self._mode)

    @property
    def padding(self) -> str | None:
        return self._padding

    def __init__(
        self,
        *,
        mode: str,
        aad: bytes | None = None,
        padding: str | None = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._mode = mode
        self._aad = aad
        self._padding = padding

    def is_aead(self) -> bool: # pragma: no cover
        return self._mode == 'GCM'

    def get_cipher(
        self,
        iv: bytes | None = None,
        tag: bytes | None = None
    ) -> Cipher[modes.CBC | modes.GCM]:
        if iv is None:
            # This is a decrypt operation and the iv is provided by
            # the input.
            iv = self.get_initialization_vector()
        if iv is None: # pragma: no cover
            raise ValueError("The `iv` parameter can not be None.")
        params: dict[str, Any] = {'initialization_vector': iv}
        if self._mode == 'GCM' and isinstance(self.content, CipherText):
            params['tag'] = self.content.tag
        return Cipher(
            algorithm=self.get_private_key(),
            mode=self.mode(**params)
        )

    def get_ciphertext(self) -> CipherText:
        if not isinstance(self.content, CipherText): # pragma: no cover
            raise TypeError("Input data is not encrypted.")
        return self.content

    def get_initialization_vector(self) -> bytes | None:
        return self.content.iv

    def get_private_key(self) -> AES:
        return self.spec.get_private_key()