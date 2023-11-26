# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

import pydantic

from .iresourcemeta import IResourceMeta

T = TypeVar('T', bound='IResource')


class IResource(pydantic.BaseModel):
    __deferred__: dict[str, Any] = pydantic.PrivateAttr({})
    _meta: IResourceMeta

    @classmethod
    def get_meta(cls) -> IResourceMeta:
        return cls._meta

    @classmethod
    def get_list_url(cls, *params: Any) -> str:
        return cls._meta.get_list_url()

    @classmethod
    def get_retrieve_url(
        cls: type[T],
        resource_id: int | str | None
    ) -> str:
        raise NotImplementedError

    def get_persist_url(self) -> str:
        raise NotImplementedError