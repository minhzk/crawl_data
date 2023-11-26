# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .fields import ResourceAnnotationsField
from .fields import ResourceLabelsField


class BaseResourceMetadata(pydantic.BaseModel):
    annotations: dict[str , str] = ResourceAnnotationsField()
    labels: dict[str, str] = ResourceLabelsField()
    tags: set[str] = set()