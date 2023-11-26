# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from headless.types import IResource
from .deferredresource import DeferredResource


T = TypeVar('T', bound='ResourceReference')


class ResourceReference:
    __module__: str = 'headless.types'
    attname: str
    model: type[IResource]
    name: str | None

    def __init__(
        self,
        model: type[IResource],
        attname: str
    ):
        self.attname = attname
        self.model = model
        self.name = None

    def add_to_class(self, cls: Any, attname: str) -> None:
        setattr(cls, attname, self)
        self.name = attname

    def __get__(
        self: T,
        obj: IResource | None,
        cls: type[IResource]
    ) -> DeferredResource | T:
        if obj is None: return self
        assert self.name is not None
        deferred = obj.__deferred__.get(self.name)
        if deferred is None:
            deferred = obj.__deferred__[self.name] = DeferredResource(
                obj._client, # type: ignore
                cls,
                self.name,
                self.model,
                getattr(obj, self.attname)
            )
        return obj.__deferred__[self.name]