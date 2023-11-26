# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from ..resource import TeamleaderResource
from .customfieldconfiguration import CustomFieldConfiguration


class CustomFieldDefinition(TeamleaderResource):
    id: str
    context: str
    type: str
    label: str = ""
    group: str | None = None
    required: bool = False
    configuration: CustomFieldConfiguration = pydantic.Field(
        default_factory=CustomFieldConfiguration
    )
    extra_option_allowed: bool = False

    class Meta(TeamleaderResource.Meta):
        base_endpoint: str = '/customFieldDefinitions'