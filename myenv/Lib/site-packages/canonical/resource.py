# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import hashlib
import inspect
from typing import Any
from typing import TypeVar

import pydantic

from .objectmeta import ObjectMeta
from .resourcemetaclass import ResourceMetaclass


T = TypeVar("T", bound="Resource")


class Resource(pydantic.BaseModel, metaclass=ResourceMetaclass):
    __abstract__: bool = True
    api_version: str
    kind: str
    metadata: ObjectMeta

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        values.setdefault('apiVersion', '%s/%s' % cls._version) # type: ignore
        values.setdefault('kind', cls.__name__)  # type: ignore
        metadata: dict[str, Any] = values.setdefault('metadata', {})
        metadata.setdefault('generation', 0)
        return values

    def __init_subclass__(
        cls,
        *,
        version: str | None = None,
        group: str | None = None,
        **kwargs: Any
    ):
        super().__init_subclass__(**kwargs)

    @classmethod
    def restore(
        cls: type[T],
        uid: int | str,
        created: datetime.datetime,
        name: str | None = None,
        annotations: dict[str, Any] | None = None,
        labels: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        spec: dict[str, Any] | None = None
    ) -> T:
        metadata = metadata or {}
        metadata.setdefault('annotations', annotations or {})
        metadata.setdefault('labels', labels or {})
        metadata.setdefault('name', name or str(uid))
        metadata.update({
            'created': created,
            'uid': uid
        })
        return cls.parse_obj({
            'metadata': metadata,
            'spec': spec or {}
        })

    @classmethod
    def new(
        cls: type[T],
        name: str | None,
        params: dict[str, Any]
    ) -> T:
        """Create a new resource."""
        metadata: dict[str, Any] = {'name': name}
        metadata.setdefault('annotations', {})
        metadata.setdefault('labels', {})
        if not metadata.get('name'):
            del metadata['name']
            metadata['generate_name'] = True
        self = cls.parse_obj({
            'metadata': {**metadata, 'uid': None},
            'spec': params
        })
        if not self.metadata.name:
            self.metadata.name = self.generate_name()
        return self

    def annotate(self, key: str, value: Any) -> None:
        """Adds an annotation to the resources' metadata."""
        if not hasattr(self.metadata, 'annotations'):
            raise TypeError(
                f'Resource {type(self).__name__} does not support '
                'annotations.'
            )
        self.metadata.annotations[key] = value

    def can_replace(self) -> bool:
        """Return a boolean indicating if the specification may be
        replaced.
        """
        raise NotImplementedError

    def compare_spec(self, spec: Any) -> bool:
        """Return a boolean indicating if the spec differs from our spec."""
        return self._hash(getattr(self, 'spec')) != self._hash(spec)

    def generate_name(self) -> str | None:
        """Generates a name for the resource. The default implementation
        returns ``None``, meaning that it does not know how to generate
        a name and defers the generation to other parts of the code.
        """
        return None

    def is_new(self) -> bool:
        """Return a boolean indicating if the object is new i.e. to the clients'
        knowledge, did not priorly exist.
        """
        return getattr(self.metadata, 'resource_version', 'pristine') == 'pristine'

    def is_pristine(self) -> bool:
        """Return a boolean indicating if the resource is pristine."""
        return self.metadata.resource_version in {'pristine', None}

    def label(self, key: str, value: str) -> None:
        """Adds a label to the resources' metadata."""
        if not hasattr(self.metadata, 'labels'):
            raise TypeError(
                f'Resource {type(self).__name__} does not support '
                'labels.'
            )
        self.metadata.labels[key] = value

    def replace(self, resource: Any) -> None:
        """Replaces the existing desired state with the given desired
        state.
        """
        if not self.can_replace():
            raise ValueError("Resource may not be replaced in its current state.")
        setattr(self, 'spec', getattr(resource, 'spec'))
        if hasattr(self, 'status'):
            self.status = None
        self.metadata.annotations = resource.metadata.annotations
        self.metadata.labels = resource.metadata.labels

    def set_default_status(self) -> None:
        """Hook to set the default status of a resource."""
        pass

    def set_status(self, new: dict[str, Any] | pydantic.BaseModel) -> None:
        """Sets the `status` property of a resource."""
        old = getattr(self, 'status', None)
        if not isinstance(old, pydantic.BaseModel):
            raise TypeError(
                f"Resource {self.__class__.__name__} does not implement the "
                "status attribute."
            )
        if isinstance(new, pydantic.BaseModel):
            new = new.dict()
        Model = getattr(self.__fields__['status'], 'type_', None)
        if not inspect.isclass(Model) or not issubclass(Model, pydantic.BaseModel):
            raise TypeError(
                f"Resource {self.__class__.__name__}.status is not a model."
            )
        setattr(self, 'status', Model.parse_obj({**old.dict(), **new}))

    def update_resource_version(self) -> None:
        """Updates the resource version in the metadata."""
        self.metadata.resource_version = bytes.hex(self._hash(self))

    def _set_default_status(self) -> None:
        self.set_default_status()

    @staticmethod
    def _hash(obj: Any) -> bytes:
        h = hashlib.sha3_256()
        if isinstance(obj, pydantic.BaseModel):
            for field in obj.__fields__.keys():
                v = getattr(obj, field)
                h.update(Resource._hash(v))
        elif isinstance(obj, str):
            h.update(str.encode(obj, encoding='utf-8'))
        elif isinstance(obj, int):
            h.update(
                int.to_bytes(obj, (obj.bit_length() + 7) // 8, 'big')
            )
        elif isinstance(obj, dict):
            for key in sorted(obj.keys()): # type: ignore
                assert isinstance(key, str)
                h.update(Resource._hash(key))
                h.update(Resource._hash(obj[key]))
        elif isinstance(obj, list):
            for item in obj: # type: ignore
                h.update(Resource._hash(item))
        elif isinstance(obj, datetime.datetime):
            h.update(Resource._hash(obj.isoformat()))
        elif obj is None:
            pass
        else:
            raise TypeError(f'Unhashable type: {repr(obj)}')
        return h.digest()