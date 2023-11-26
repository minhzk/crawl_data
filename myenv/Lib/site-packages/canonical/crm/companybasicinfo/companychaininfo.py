# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical import ResourceName


class CompanyChainInfo(pydantic.BaseModel):
    is_branch: bool = pydantic.Field(
        default=False,
        alias='isBranch',
        title="Is branch?",
        description=(
            "Indicates if the company is part of a chain or franchise, "
            "and is a branch."
        )
    )

    parent: ResourceName | None = pydantic.Field(
        default=None,
        title="Parent",
        description=(
            "Identifies the chain or franchise headquarters."
        )
    )

    class Config:
        allow_population_by_field_name: bool = True