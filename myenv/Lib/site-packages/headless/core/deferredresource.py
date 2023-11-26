# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generator

from headless.types import IClient
from headless.types import IResource


class DeferredResource:
    __module__: str = 'headless.types'
    __attname: str
    __client: IClient[Any, Any]
    __model: type[IResource]
    __params: tuple[Any, ...]
    __parent: type[IResource]
    __instance: IResource | None

    def __init__(
        self,
        client: IClient[Any, Any],
        parent: type[IResource],
        attname: str,
        model: type[IResource],
        *params: Any
    ):
        self.__attname = attname
        self.__client = client
        self.__instance = None
        self.__model = model
        self.__params = params
        self.__parent = parent

    async def __fetch(self) -> Any:
        if self.__instance is None:
            self.__instance = await self.__client.retrieve(self.__model, *self.__params)
        return self.__instance

    def __await__(self) -> Generator[Any, Any, Any]:
        return self.__fetch().__await__()

    def __getattr__(self, attname: str) -> Any:
        if self.__instance is not None:
            return getattr(self.__instance, attname)
        raise RuntimeError(
            f'To access {self.__parent.__name__}.{self.__attname} it must '
            'first be awaited.'
        )

    def __repr__(self) -> str:
        return repr(self.__instance)\
            if self.__instance is not None\
            else super().__repr__()