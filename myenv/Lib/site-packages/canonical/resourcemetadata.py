# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from .fields import ResourceAnnotationsField
from .resourcename import ResourceName


class ResourceMetadata(pydantic.BaseModel):
    name: ResourceName
    annotations: dict[str , str] = ResourceAnnotationsField()
    labels: dict[str, str] = {}
    tags: set[str] = set()

    @classmethod
    def _qualname(cls, namespace: str | None, name: str) -> str:
        qualname = name
        if namespace is not None:
            qualname = f'{namespace}/{name}'
        return qualname

    def annotate(self, name: str, value: Any, namespace: str | None = None) -> None:
        self.annotations[self._qualname(namespace, name)] = value
    
    def get_label(self, name: str, namespace: str | None = None) -> Any:
        """Return the label in the optional namespace."""
        return self.labels.get(self._qualname(namespace, name))

    def is_annotated(self, name: str, namespace: str | None = None) -> bool:
        """Return a boolean indicating if the resource has the given
        annotation.
        """
        return self._qualname(namespace, name) in self.annotations

    def is_tagged(self, value: str | set[str]) -> bool:
        """Return a boolean indicating if the resource has the given
        tag.
        """
        if isinstance(value, str):
            value = {value}
        return bool(value & self.tags)

    def label(self, name: str, value: Any, namespace: str | None = None) -> None:
        self.labels[self._qualname(namespace, name)] = value

    def tag(self, value: str) -> None:
        self.tags.add(value)