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

from .digest import Digest
from .keyoperationtype import KeyOperationType
from .ioperationperformer import IOperationPerformer
from .iprovider import IProvider
from .message import Message


class Signer(IOperationPerformer):
    __module__: str = 'ckms.types'
    algorithm: str | None
    provider: IProvider
    kid: Any

    @IOperationPerformer.must_allow(KeyOperationType.sign)
    def sign(
        self,
        message: bytes | Digest | Message,
    ) -> bytes | Awaitable[bytes]:
        """Sign `message` using the configured algorithm."""
        assert hasattr(self, 'algorithm')
        assert hasattr(self, 'provider')
        assert isinstance(self.provider, IProvider)
        assert self.algorithm is not None
        digest = self.provider.get_hashing_algorithm(self.algorithm)
        if not isinstance(message, (Digest, Message)):
            message = Message(buf=message)
        if digest is not None and not message.digestmod:
            message.set_digest_algorithm(digest)
        return self.provider.sign(
            key=self,
            algorithm=self.algorithm,
            message=message
        )

    def get_digest_oid(self) -> str | None:
        """Return the OID of the signing algorithm."""
        raise NotImplementedError