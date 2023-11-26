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

import pydantic
from cryptography.hazmat.primitives.ciphers import algorithms

from ckms.core import const
from ckms.types import IKeyInspector
from ckms.types import IProvider
from ckms.types import KeyUseType
from .contentencryptionkey import ContentEncryptionKey
from .hmac import HMAC
from .localkey import LocalKey
from .localkeyspecification import LocalKeySpecification
from .parameterlesskey import ParameterLessKey
from .transientkey import TransientKey


class SymmetricKeySpecification(LocalKeySpecification):
    kty: Literal['oct'] = 'oct'
    use: KeyUseType | None = None
    key: ContentEncryptionKey | LocalKey | TransientKey | ParameterLessKey | None

    @pydantic.root_validator(pre=True)
    def set_key_params(cls, values: dict[str, Any]) -> dict[str, Any]:
        algorithm = values.get('algorithm')
        if algorithm is not None and not bool(values.get('key')):
            # TODO: Very ugly
            if str.startswith(algorithm, 'A128'):
                length = 16
            elif str.startswith(algorithm, 'A192'):
                length = 24
            elif str.startswith(algorithm, 'A256'):
                length = 32
            else:
                raise NotImplementedError(algorithm)
            values['key'] = {'length': length}

        # If the key is specified by path, update the mapping with
        # encoding=binary to differentiate from PEM-encoded keys.
        key: dict[str, Any] | None = values.get('key')
        if key is not None:
            key['encoding'] = 'binary'
        return values

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
        elif values.get('use') == 'sig':
            values['algorithm'] = const.DEFAULT_SYMMETRIC_SIGNING_ALGORITHM
        elif values.get('use') == 'enc':
            values['algorithm'] = const.DEFAULT_SYMMETRIC_ENCRYPTION_ALGORITHM

    def get_private_bytes(self) -> bytes:
        private = self.get_private_key()
        return private.key

    def get_private_key(self) -> algorithms.AES | HMAC:
        assert isinstance(self.key, (algorithms.AES, HMAC)), type(self.key)
        return self.key

    async def setup_key(self) -> algorithms.AES | HMAC:
        k: bytes | algorithms.AES | HMAC = await super().setup_key()
        if isinstance(k, (algorithms.AES, HMAC)):
            return k
        assert isinstance(k, bytes), type(k) # nosec
        if self.use == 'sig':
            k = HMAC(k)
        elif self.use == 'enc':
            k = algorithms.AES(k)
        else:
            raise NotImplementedError(self.use)
        assert isinstance(k, (algorithms.AES, HMAC)) # nosec
        return k