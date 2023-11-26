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

from ..resourcename import ResourceName
from ..resourcemetadata import ResourceMetadata
from .dto import DTO


class VersionedDTO(pydantic.BaseModel):
    __root__: DTO

    @property
    def metadata(self) -> ResourceMetadata:
        return self.__root__.metadata

    @property
    def name(self) -> ResourceName:
        return self.__root__.metadata.name

    @property
    def resource_id(self) -> str:
        return self.metadata.name.id

    @classmethod
    def parse(
        cls,
        *,
        name: ResourceName = ResourceName.null(),
        spec: dict[str, Any] | None = None,
        version: str | None = None,
        annotations: dict[str, str] | None = None,
        labels: dict[str, str] | None = None,
        tags: set[str] | None = None
    ):
        spec = spec or {}
        params: dict[str, Any] = {
            'kind': cls.__name__,
            'metadata': {
                'name': name,
                'annotations': annotations or {},
                'labels': labels or {},
                'tags': tags or set()
            },
            'spec': spec
        }
        if version is not None:
            params['apiVersion'] = version
        return cls.parse_obj(params)

    def annotate(self, name: str, value: Any, namespace: str | None = None) -> None:
        self.__root__.metadata.annotate(name, value, namespace)

    def assign(self, name: ResourceName) -> None:
        """Assign an identity to the DTO (by settings the :attr:`resource_id`)
        attribute.
        """
        self.metadata.name = name

    def get_label(self, name: str, namespace: str | None = None) -> Any:
        """Return the label in the optional namespace."""
        return self.metadata.get_label(name, namespace=namespace)

    def has_identity(self) -> bool:
        """Return a boolean indicating if the underlying resource has an
        identity.
        """
        return self.metadata.name != ResourceName.null()

    def is_annotated(self, name: str, namespace: str | None = None) -> bool:
        """Return a boolean indicating if the resource has the given
        annotation.
        """
        return self.__root__.metadata.is_annotated(name, namespace=namespace)

    def is_tagged(self, value: str | set[str]) -> bool:
        """Return a boolean indicating if the resource has the given
        tag.
        """
        return self.__root__.metadata.is_tagged(value)

    def label(self, name: str, value: Any, namespace: str | None = None) -> None:
        self.__root__.metadata.label(name, value, namespace)

    def tag(self, value: str) -> None:
        self.__root__.metadata.tag(value)