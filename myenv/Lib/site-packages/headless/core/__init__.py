# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from .deferredresource import DeferredResource
from .linearbackoff import LinearBackoff
from .resource import Resource # type: ignore
from .resourcemeta import ResourceMeta
from .resourcemetaclass import ResourceMetaclass
from .resourcereference import ResourceReference


__all__: list[str] = [
    'DeferredResource',
    'LinearBackoff',
    'Resource',
    'ResourceMeta',
    'ResourceMetaclass',
    'ResourceReference',
]


def Reference(model: type[Resource], attname: str) -> Any:
    return ResourceReference(model, attname)