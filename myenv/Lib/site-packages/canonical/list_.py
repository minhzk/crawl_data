# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Literal

import pydantic

from .listmeta import ListMeta


class _EntityList:

    def __init__(self, getitem: Callable[..., Any]):
        self._getitem = getitem

    def __getitem__(self, model: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        return self._getitem(model)


@_EntityList
def List(model: type[pydantic.BaseModel]):
    name = f'{model.__name__}List'
    return type(name, (pydantic.BaseModel,), {
        'api_version': pydantic.Field(
            default='v1',
            alias='apiVersion',
            title='API Version',
            description=(
                "APIVersion defines the versioned schema of this representation of "
                "an object. Servers should convert recognized schemas to the latest "
                "internal value, and may reject unrecognized values."
            )
        ),
        'kind': pydantic.Field(
            default=name,
            title='Kind',
            description=(
                "Kind is a string value representing the REST resource this "
                "object represents. Servers may infer this from the endpoint "
                "the client submits requests to. Cannot be updated. In "
                "CamelCase. "
            )
        ),
        'metadata': pydantic.Field(
            default_factory=ListMeta,
            title='Metadata',
            description="Standard list metadata."
        ),
        'items': pydantic.Field(
            default=[],
            title='Items',
            description=f'List of **{model.__name__}** objects.'
        ),
        '__annotations__': {
            'api_version': str,
            'kind': Literal[f'{model.__name__}List'],
            'metadata': ListMeta,
            'items': list[model]
        }
    })