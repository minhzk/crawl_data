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
"""Declares :class:`RSAOperation`."""
from typing import Any

from .operation import Operation


class RSAOperation(Operation):
    """Represents a cryptopgraphic operation using an RSA key."""
    __module__: str = 'ckms.core.types'
    aad: bytes | None = None
    _digest: str
    _padding: str
    _signature: bytes | None

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def padding(self) -> str:
        return self._padding

    @property
    def signature(self) -> bytes | None:
        return self._signature

    def __init__(
        self,
        *,
        digest: str,
        padding: str,
        signature: bytes | None = None, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._digest = digest
        self._padding = padding
        self._signature = signature

    async def get_digest(self) -> bytes:
        """Return a digest of the message."""
        return await self.content.digest(algorithm=self.digest)