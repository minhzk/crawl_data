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
from typing import TypeAlias

from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import x25519

from ckms.core import const
from ckms.types import EdwardsCurveType
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import KeyUseType
from .localkey import LocalKey
from .localkeyspecification import LocalKeySpecification
from .parameterlesskey import ParameterLessKey


OKPPublic: TypeAlias = (
    ed448.Ed448PublicKey |
    ed25519.Ed25519PublicKey |
    x448.X448PublicKey |
    x25519.X25519PublicKey
)


OKPPrivate: TypeAlias = (
    ed448.Ed448PrivateKey |
    ed25519.Ed25519PrivateKey |
    x448.X448PrivateKey |
    x25519.X25519PrivateKey
)


class EdwardsCurveKeySpecification(LocalKeySpecification):
    kty: Literal['OKP'] = 'OKP'
    #algorithm: types.EdwardsCurveAlgorithmType | None
    curve: EdwardsCurveType | None
    key: LocalKey | ParameterLessKey = ParameterLessKey()
    use: KeyUseType

    @classmethod
    def autodiscover(
        cls,
        provider: IProvider,
        inspector: IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('use') and not values.get('curve'):
            raise ValueError(
                "Specify either the `use` parameter the `curve` parameter."
            )
        if values.get('curve') in {'Ed448', 'Ed25519'}:
            values['use'] = 'sig'
        elif values.get('curve') in {'X448', 'X25519'}:
            values['use'] = 'enc'
        elif values.get('use') == 'sig':
            values['curve'] = const.DEFAULT_ED_SIGNING_CURVE
        elif values.get('use') == 'enc':
            values['curve'] = const.DEFAULT_ED_ENCRYPTION_CURVE
        else:
            raise ValueError("Unable to infer key parameters.")
        if values['use'] == 'sig':
            values['algorithm'] = 'EdDSA'
        if values['use'] == 'enc' and not values.get('algorithm'):
            values['algorithm'] = const.DEFAULT_ED_ENCRYPTION_ALGORITHM

    def get_public_key(self) -> OKPPublic:
        assert isinstance(self.key, OKPPrivate)
        return self.key.public_key()