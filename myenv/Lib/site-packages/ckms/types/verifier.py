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
from typing import Awaitable
from typing import Any

from .digest import Digest
from .ioperationperformer import IOperationPerformer
from .iprovider import IProvider
from .keyoperationtype import KeyOperationType
from .message import Message


class Verifier(IOperationPerformer):
    __module__: str = 'ckms.types'
    algorithm: Any
    provider: IProvider

    @IOperationPerformer.must_allow(KeyOperationType.verify)
    def verify(
        self,
        signature: bytes,
        message: bytes | Digest | Message,
    ) -> bool | Awaitable[bool]:
        """Verify that `signature` was created using this key from the given
        `message`.
        """
        assert isinstance(self.provider, IProvider)
        assert self.algorithm is not None
        digest = self.provider.get_hashing_algorithm(self.algorithm)
        if not isinstance(message, (Digest, Message)):
            message = Message(buf=message)
        if digest is not None and not message.digestmod:
            message.set_digest_algorithm(digest)
        return self.provider.verify(
            algorithm=self.algorithm,
            key=self,
            message=message,
            signature=signature
        )