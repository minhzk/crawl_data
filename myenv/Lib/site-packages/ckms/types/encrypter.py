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
from typing import Any
from typing import Awaitable

from .ciphertext import CipherText
from .ioperationperformer import IOperationPerformer
from .iprovider import IProvider
from .keyoperationtype import KeyOperationType
from .plaintext import PlainText


class Encrypter(IOperationPerformer):
    __module__: str = 'ckms.core.types'
    algorithm: str | None
    kid: Any
    provider: IProvider

    @IOperationPerformer.must_allow(KeyOperationType.encrypt)
    def encrypt(
        self,
        pt: bytes | PlainText,
        **kwargs: Any
    ) -> CipherText | Awaitable[CipherText]:
        """Encrypt `pt` using the configured algorithm."""
        assert hasattr(self, 'algorithm')
        assert hasattr(self, 'provider')
        assert isinstance(self.provider, IProvider)
        assert self.algorithm is not None
        if not isinstance(pt, PlainText):
            pt = PlainText(pt)
        return self.provider.encrypt(
            key=self,
            algorithm=self.algorithm,
            plaintext=pt,
            **kwargs
        )

    @IOperationPerformer.must_allow(KeyOperationType.wrapKey)
    def wrap(
        self,
        key: bytes | PlainText,
        **kwargs: Any
    ) -> CipherText | Awaitable[CipherText]:
        assert hasattr(self, 'algorithm')
        assert hasattr(self, 'provider')
        assert isinstance(self.provider, IProvider)
        assert self.algorithm is not None
        if not isinstance(key, PlainText):
            key = PlainText(key)
        return self.provider.wrap(
            key=self,
            algorithm=self.algorithm,
            wrap=key,
            **kwargs
        )

    def is_aead(self) -> bool:
        """Return a boolean indicating if the operator supports Authenticated
        Encryption with Associated Data (AEAD).
        """
        raise NotImplementedError