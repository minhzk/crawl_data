# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from canonical.fields import ResourceKindField
from canonical.resourcemetadata import ResourceMetadata


class CompanyBasicInfoBase(pydantic.BaseModel):
    kind: Literal['CompanyBasicInfo'] = ResourceKindField()
    metadata: ResourceMetadata = pydantic.Field(
        default=...,
        title="Metadata",
        description=(
            "Standard object's metadata. More info: https://git.k8s.io"
            "/community/contributors/devel/sig-architecture/api-conventions.md"
            "#metadata"
        )
    )