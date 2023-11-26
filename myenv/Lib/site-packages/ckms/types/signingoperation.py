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
"""Declares :class:`SigningOperation`."""
from typing import Any

from .operation import Operation


class SigningOperation(Operation):
    """The base class for all signing operations."""
    __module__: str = 'ckms.core.types'
    _signature: bytes | None

    @property
    def signature(self) -> bytes | None:
        return self._signature

    def __init__(self, *, signature: bytes | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self._signature = signature