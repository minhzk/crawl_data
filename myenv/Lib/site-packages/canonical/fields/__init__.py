# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic


__all__: list[str] = [
    'ResourceAnnotationsField',
    'ResourceKindField',
    'ResourceLabelsField',
    'ResourceVersionField',
]


def ResourceVersionField(version: str) -> Any:
    return pydantic.Field(
        default=version,
        alias='apiVersion',
        title='API Version',
        description=(
            "The `apiVersion` property defines the versioned schema of this "
            "representation of an object. Servers should convert recognized "
            "schemas to the latest internal value, and may reject "
            "unrecognized values. More info: https://git.k8s.io/community/"
            "contributors/devel/sig-architecture/api-conventions.md#resources"
        ),
        enum=[version]
    )


def ResourceKindField() -> Any:
    return pydantic.Field(
        default=...,
        title="Kind",
        description=(
            "Kind is a string value representing the conceptual model, entity or "
            "REST resource this object represents. Servers may infer this from "
            "the endpoint the client submits requests to. Cannot be updated. "
            "In `CamelCase`."
        )
    )


def ResourceAnnotationsField() -> Any:
    return pydantic.Field(
        default_factory=dict,
        title="Annotations",
        description=(
            "Annotations is an unstructured key value map stored with "
            "a resource that may be set by external tools to store and "
            "retrieve arbitrary metadata. They are not queryable and "
            "should be preserved when modifying objects."
        )
    )


def ResourceLabelsField() -> Any:
    return pydantic.Field(
        default_factory=dict,
        title="Labels",
        description=(
            "Map of string keys and values that can be used to "
            "organize and categorize (scope and select) objects. "
            "May match selectors of resources and services."
        )
    )