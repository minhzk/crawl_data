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
"""Declares :class:`CipherText`."""
from typing import Any

from .data import Data


class CipherText(Data):
    """The result of an encryption operation."""
    __module__: str = 'ckms.types'
    aad: bytes | None
    content: bytes
    iv: bytes | None
    tag: bytes | None

    def __init__(
        self,
        *,
        aad: bytes | None = None,
        iv: bytes | None = None,
        tag: bytes | None = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.aad = aad
        self.iv = iv
        self.tag = tag
