# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum


class ProductFeatureConstraint(str, enum.Enum):
    """Specifies how a feature (or a set of features) should be
    validated across all variants of a product.
    """
    #: No constraints are applied to the :term:`ProductFeature`.
    NONE                = 'NONE'

    #: Must be unique for its resource.
    UNIQUE              = 'UNIQUE'

    #: Must be unique a unique set of features.
    UNIQUE_COMBINATION  = 'UNIQUE_COMBINATION'

    #: Must be consistent.
    CONSISTENT          = 'CONSISTENT'
