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
import pathlib
from typing import Any
from typing import Literal

import pydantic
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .localkeyspecification import LocalKeySpecification


class LocalKey(pydantic.BaseModel):
    path: str | pathlib.Path
    password: bytes | None
    encoding: Literal['binary', 'pem'] = 'pem'

    async def setup(self, spec: LocalKeySpecification) -> Any:
        if self.encoding not in ('binary', 'pem'):
            raise NotImplementedError(self.encoding)
        decode: Any = lambda x, *a, **k: x # type: ignore
        if self.encoding == 'pem':
            decode = load_pem_private_key
        with open(self.path, 'rb') as f:
            return decode(f.read(), self.password)