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
"""Declares :class:`JSONB64`"""
import json
from typing import Any
from typing import Callable
from typing import Generator

from ckms.utils import b64decode


class JSONB64(dict[str, Any]):
    """A :mod:`pydantic` field type that serializes from URL-safe, base64-encoded
    input data.
    """
    __module__: str = 'ckms.core.models'

    @classmethod
    def __get_validators__(
        cls
    ) -> Generator[Callable[..., 'JSONB64'], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: bytes) -> 'JSONB64':
        if isinstance(value, cls): # pragma: no cover
            return value

        return cls(**json.loads(bytes.decode(b64decode(value), 'utf-8')))

    def __repr__(self) -> str: # pragma: no cover
        return f'JSONB64({super().__repr__()})'