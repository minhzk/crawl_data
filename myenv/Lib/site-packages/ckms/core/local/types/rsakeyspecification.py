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

from cryptography.hazmat.primitives.asymmetric import rsa

from ckms.core import const
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import KeyUseType
from .localkey import LocalKey
from .localkeyspecification import LocalKeySpecification
from .transientkey import TransientKey


class RSAKeySpecification(LocalKeySpecification):
    kty: Literal['RSA'] = 'RSA'
    use: KeyUseType | None = None
    key: LocalKey | TransientKey | rsa.RSAPrivateKey

    @classmethod
    def autodiscover(
        cls,
        provider: IProvider,
        inspector: IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        if not values.get('use') and not values.get('algorithm'):
            raise ValueError(
                "Unable to infer the key algorithm. Specify either the "
                "`algorithm` or `use` parameter."
            )
        if values.get('use') == 'sig':
            values['algorithm'] = const.DEFAULT_RSA_SIGNING_ALG
        elif values.get('use') == 'enc':
            values['algorithm'] = const.DEFAULT_RSA_ENCRYPTION_ALG
        else:
            values['use'] = inspector.get_algorithm_use(values['algorithm'])

    def get_public_key(self) -> rsa.RSAPublicKey:
        assert isinstance(self.key, rsa.RSAPrivateKey)
        return self.key.public_key()