# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum


class ProductFeatureType(str, enum.Enum):
    #: Standard production feature; consistent accross all variants.
    STANDARD = 'STANDARD'

    #: Mandatory feature as part of the product definition. A
    #: required feature is consistent across all variants.
    REQUIRED = 'REQUIRED'

    #: The feature needs to be selected from a controlled
    #: vocabulary.
    SELECTABLE = 'SELECTABLE'

    #: The feature is optional.
    OPTIONAL = 'OPTIONAL'