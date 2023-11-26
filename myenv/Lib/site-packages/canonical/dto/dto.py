# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied
from typing import Any
from typing import Literal

import pydantic
import pydantic.main

from ..fields import ResourceVersionField
from ..resourcemetadata import ResourceMetadata
from .dtometaclass import DTOMetaclass


class DTO(pydantic.BaseModel, version='v1', metaclass=DTOMetaclass):
    """A Data Transfer Object (DTO) is an object that carries data between
    processes.
    """
    api_version: Literal['v1'] = ResourceVersionField('v1')
    kind: str
    metadata: ResourceMetadata = pydantic.Field(
        default=...,
        title="Metadata",
        description="Standard object's metadata."
    )
    spec: Any