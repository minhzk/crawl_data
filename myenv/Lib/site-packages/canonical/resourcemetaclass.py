# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from types import EllipsisType
from typing import Any
from typing import Literal
from typing import TypeVar

import inflect
import pydantic

from .objectmeta import BaseMeta
from .objectmeta import ObjectMeta


T = TypeVar('T')
engine = inflect.engine()


class Config:
    annotations: bool = False
    group: str
    named: bool = False
    namespaced: bool = False
    labels: bool = False
    pluralname: str
    version: str

    @classmethod
    def dict(cls) -> dict[str, Any]:
        return {
            'annotations': cls.annotations,
            'group': cls.group,
            'named': cls.named,
            'namespaced': cls.namespaced,
            'labels': cls.labels,
            'pluralname': cls.pluralname,
            'version': cls.version
        }


class ResourceMetaclass(pydantic.main.ModelMetaclass):

    def __new__(
        cls,
        name: str,
        bases: tuple[type[Any]],
        namespace: dict[str, Any],
        **params: Any
    ) -> 'ResourceMetaclass':
        if not namespace.pop('__abstract__', False):
            ResourceConfig: type[Any] | None = namespace.get('Config')
            annotations = namespace.setdefault('__annotations__', {})

            # To support dynamic subclassing, inspect the bases to determine if this
            # class directly inherits from a Resource subclass. Use an instance
            # check instead of a subclass check to remove the need for circular
            # imports. Reconstruct the subclass parameters from the existing class.
            for b in bases:
                if isinstance(b, ResourceMetaclass) and hasattr(b, '_version'):
                    group, version = api_version = b._version # type: ignore

                    # These are needed to initialize the superclass if this is a
                    # third-generation subclass of Resource.
                    params['group'] = group
                    params['version'] = version

                    # Get the Config class from parent.
                    ResourceConfig = getattr(b, 'Config', None)

                    break
            else:
                group = params.get('group')
                version = api_version = params.get('version')
                ResourceConfig = namespace.get('Config')
            if group is not None:
                api_version = f'{group}/{version}'

            # Create or update the config.
            if ResourceConfig is None:
                ResourceConfig = namespace['Config'] = type('Config', (Config,), {})
            assert ResourceConfig is not None
            attrs: dict[str, Any] = {
                'name': str.lower(name),
                **{k: v for k, v in Config.__dict__.items() if not k.startswith('_')},
                **{k: v for k, v in ResourceConfig.__dict__.items()
                if not k.startswith('_')},
                'group': group,
                'version': version
            }
            attrs.setdefault('pluralname', engine.plural(attrs['name']))
            ResourceConfig = namespace['Config'] = type('Config', (Config,), attrs)

            # Create the `spec` field if the user has not specified it.
            if annotations.get('spec'):
                ResourceSpec: type[pydantic.BaseModel] = annotations['spec']
                assert isinstance(ResourceSpec, pydantic.main.ModelMetaclass)
                namespace.setdefault(
                    'spec',
                    pydantic.Field(
                        default=...,
                        title=ResourceSpec.__name__,
                        description=(
                            f'The `spec` field defines the specification of the '
                            f'desired behavior or state of the **{name}**.'
                        )
                    )
                )

            # Ensure that the apiVersion, kind and metadata fields are present. Defaults
            # and constraints are set during subclass initialization.
            Metadata = annotations.setdefault('metadata', ObjectMeta)
            annotations['metadata'] = Metadata.clone(**ResourceConfig.dict())
            annotations.update({
                'api_version': Literal[api_version], # type: ignore
                'kind': Literal[name], # type: ignore
            })
            namespace.update({
                '__annotations__': annotations,
                '_version': (group, version),
                'api_version': pydantic.Field(
                    alias='apiVersion',
                    description=(
                        'The `apiVersion` field defines the versioned schema of this '
                        'representation of an object. Servers should convert '
                        'recognized schemas to the latest internal value, and may '
                        'reject unrecognized values.'
                    )
                ),
                'kind': pydantic.Field(
                    description=(
                        'The `kind` field is a string value representing the REST resource this '
                        'object represents. Servers may infer this from the endpoint '
                        'the client submits requests to. Cannot be updated. '
                        'In `CamelCase`.'
                    )
                ),
                'metadata': pydantic.Field(
                    default=...,
                    title='Metadata',
                    description="Standard object's metadata."
                )
            })

            # Determine if there is a status model.
            ResourceStatus: Any | None = namespace.pop('Status', None)
            if ResourceStatus is not None:
                annotations.update({
                    'status': ResourceStatus.model | None
                })
                namespace.update({
                    'status': pydantic.Field(
                        default=None,
                        title='Status',
                        description=f'Most recently observed status of the `{name}`.'
                    )
                })

        # Do not pass the class parameters if the parent is not a Resource, because
        # it confuses pydantic (TODO).
        if bases and not isinstance(bases[-1], ResourceMetaclass):
            params = {}
        new_cls = super().__new__(cls, name, bases, namespace) # type: ignore
        return new_cls # type: ignore

    def __getitem__(
        self: T,
        k: EllipsisType | tuple[EllipsisType, bool]
    ) -> T:
        namespace: dict[str, Any] = {}
        config: type[Config] = getattr(self, 'Config', Config)
        return type(self.__name__, (self,), { # type: ignore
            **namespace,
            'Config': config,
            '__annotations__': {
                'metadata': BaseMeta.clone(
                    pristine=True,
                    **config.dict()
                )
            }
        })