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

import pydantic

from .resourcemeta import ResourceMeta
from .resourcereference import ResourceReference


T = TypeVar('T', bound='ResourceMetaclass')


class ResourceMetaclass(pydantic.main.ModelMetaclass):
    __module__: str = 'headless.core'

    def __new__(
        cls: type[T],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **params: dict[str, Any]
    ) -> T:
        refs: dict[str, ResourceReference] = {}
        is_abstract = namespace.pop('__abstract__', False)
        if not is_abstract:
            annotations: dict[str, type] = namespace.get('__annotations__') or {}
            meta = namespace.pop('Meta', None)
            if meta is None:
                raise TypeError(
                    f'{name} must define an inner Meta class describing the '
                    'resource endpoints.'
                )
            namespace['_meta'] = meta = ResourceMeta.frominnermeta(name, meta)

            # Remove references to not confuse pydantic.
            for k in list(namespace.keys()):
                if not isinstance(namespace[k], ResourceReference):
                    continue
                refs[k] = namespace.pop(k)
                annotations.pop(k, None)

        new_class = super().__new__(cls, name, bases, namespace, **params) # type: ignore

        # Re-add the ResourceRefenrce objects to the class.
        if not is_abstract:
            for attname, ref in refs.items():
                ref.add_to_class(new_class, attname)

        return new_class # type: ignore