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
# type: ignore
"""Declares :class:`BaseKeySpecification`."""
from typing import Any

import pydantic

from ckms import core
from ckms.types import IKeySpecification
from ckms.types import IProvider


class BaseKeySpecification(pydantic.BaseModel, IKeySpecification):
    """The base class for all provider key configurations."""
    __module__: str = 'ckms.core.types'

    @pydantic.validator('provider', allow_reuse=True, check_fields=False)
    def _validate_provider(cls, value: str | IProvider) -> IProvider:
        assert value is not None # nosec
        assert value != 'none'
        if isinstance(value, str): # pragma: no cover
            value = core.provider(value)
        return value

    def can_decrypt(self) -> bool:
        """Return a boolean indicating if the key may be used to
        perform encryption operations.
        """
        return self.use == 'enc'

    def can_encrypt(self) -> bool:
        """Return a boolean indicating if the key may be used to
        perform encryption operations.
        """
        return self.use == 'enc'

    def can_sign(self) -> bool:
        """Return a boolean indicating if the key may be used to
        create digital signatures.
        """
        return self.use == "sig"

    def is_asymmetric(self) -> bool:
        """Return a boolean indicating if the key is an asymmetric
        algorithm.
        """
        return str(self.kty) in {"EC", "OKP", "RSA"}

    def is_symmetric(self) -> bool:
        """Return a boolean indicating if the key is a symmetric
        algorithm.
        """
        return self.kty in {"oct"}

    def is_loaded(self) -> bool: # pragma: no cover
        """Return a boolean indicating if the metadata describing the
        key is retrieved.
        """
        return self.loaded

    def is_public(self) -> bool:
        """Return a boolean indicating if this specification represent
        a public key.
        """
        return False

    class Config:
        arbitrary_types_allowed: bool = True