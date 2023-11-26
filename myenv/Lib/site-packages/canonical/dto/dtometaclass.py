# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic
import pydantic.main

from ..fields import ResourceKindField


class DTOMetaclass(pydantic.main.ModelMetaclass):

    def __new__(
        cls,
        name: str,
        bases: tuple[type[Any]],
        namespace: dict[str, Any],
        version: str,
        **params: Any
    ) -> 'DTOMetaclass':
        annotations: dict[str, type] = namespace.setdefault('__annotations__', {})
        if not namespace.pop('__abstract__', False):
            params.setdefault('allow_population_by_field_name', True)
            params.setdefault('title', str.title(version))
            if not namespace.get('Config'):
                namespace['Config'] = type('Config', (object,), params)
            annotations['kind'] = Literal[name] # type: ignore
            namespace['kind'] = ResourceKindField()

        new_cls = super().__new__(cls, name, bases, namespace) # type: ignore
        return new_cls # type: ignore