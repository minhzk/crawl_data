# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from .productidentifier import ProductIdentifier


class SKU(ProductIdentifier):
    kind: Literal['sku'] = pydantic.Field(
        default=...,
        title="Kind",
        description="Specifies the kind of product identifier."
    )