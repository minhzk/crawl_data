# Copyright 2022 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any
from typing import Literal

from cryptography.hazmat.primitives.asymmetric import ec

from ckms.core import const
from ckms.types import EllipticCurveType
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import KeyUseType
from .localkey import LocalKey
from .localkeyspecification import LocalKeySpecification
from .parameterlesskey import ParameterLessKey


class EllipticCurveKeySpecification(LocalKeySpecification):
    kty: Literal['EC'] = 'EC'
    #algorithm: types.EllipticCurveAlgorithmType | None = None
    curve: EllipticCurveType | None = None
    use: KeyUseType | None = None
    key: ec.EllipticCurvePrivateKey | LocalKey | ParameterLessKey = ParameterLessKey()

    @classmethod
    def autodiscover(
        cls,
        provider: IProvider,
        inspector: IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('algorithm') and not values.get('use'):
            raise ValueError(
                "Specify either the `algorithm` parameter or the "
                "`use` parameter."
            )
        if values.get('algorithm'):
            values['use'] = inspector.get_algorithm_use(values['algorithm'])
        elif values.get('use') == 'sig' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_EC_SIGNING_ALGORITHM
        elif values.get('use') == 'enc' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_EC_ENCRYPTION_ALGORITHM
        else:
            raise ValueError("Unable to infer key parameters.")
        if not values.get('curve'):
            values['curve'] = inspector.get_algorithm_curve(values['algorithm'])

    def get_public_key(self) -> ec.EllipticCurvePublicKey:
        assert isinstance(self.key, ec.EllipticCurvePrivateKey)
        return self.key.public_key()