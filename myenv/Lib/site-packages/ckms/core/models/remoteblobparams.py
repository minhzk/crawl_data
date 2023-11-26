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
"""Declares :class:`RemoteBlobParams`."""
from typing import Any
from typing import Generator

import pydantic


class RemoteBlobParams(pydantic.BaseModel):
    __module__: str = 'ckms.types'
    provider: str
    params: dict[str, Any] = {}

    def __init__(self, **kwargs: Any):
        params = kwargs.setdefault('params', {})
        for name in list(kwargs.keys()):
            if name in self.__fields__:
                continue
            params[name] = kwargs.pop(name)
        super().__init__(**kwargs)

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]: # type: ignore
        data = super().dict(*args, **kwargs)
        data.update(data.pop('params', {}))
        return data

    async def get_content(self) -> bytes:
        """Return a byte-sequence returning the content of the
        remote blob.
        """
        raise NotImplementedError

    def __await__(self) -> Generator[Any, None, bytes]: # pragma: no cover
        return self.get_content().__await__()