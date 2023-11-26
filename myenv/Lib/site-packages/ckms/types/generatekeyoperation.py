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
"""Declares :class:`GenerateKeyOperation`."""
from typing import Any

from .operation import Operation
from .generatekeyspec import GenerateKeySpec
from .generatekeyspec import KeyType


class GenerateKeyOperation(Operation):
    """Represents an key generation operation."""
    __module__: str = 'ckms.types'
    spec: KeyType

    def __init__(self, **spec: Any):
        self.spec = GenerateKeySpec.parse_spec(spec)