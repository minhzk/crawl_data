# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class ListMeta(pydantic.BaseModel):
    resource_version: str | None = pydantic.Field(
        default=None,
        alias='resourceVersion',
        title='Resource Version',
        description=(
            "String that identifies the server's internal version of this object "
            "that can be used by clients to determine when objects have changed. "
            "Value must be treated as opaque by clients and passed unmodified "
            "back to the server. Populated by the system. Read-only. "
        )
    )

    self_link: str | None = pydantic.Field(
        default=None,
        alias='selfLink',
        title='Self Link',
        description=(
            "SelfLink is a URL representing this object. Populated by the system. Read-only."
        )
    )