# Copyright 2018 Cochise Ruhulessin
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
import functools
from typing import Any

from .keyoperationtype import KeyOperationType
from .forbiddenoperation import ForbiddenOperation


class IOperationPerformer:
    __module__: str = 'ckms.types'
    algorithm: Any
    tags: set[str]
    use: Any

    @staticmethod
    def must_allow(op: KeyOperationType) -> Any:
        def decorator_factory(func: Any) -> Any:
            @functools.wraps(func)
            def f(self: IOperationPerformer, *args: Any, **kwargs: Any) -> Any:
                if not self.can_perform(op) and not kwargs.pop('force', False):
                    raise ForbiddenOperation(op)
                return func(self, *args, **kwargs)
            return f
        return decorator_factory

    def allows_algorithm(self, algorithm: str) -> bool:
        """Return a boolean indicating if the given algorithm may be used with
        the key.
        """
        return self.algorithm == algorithm

    def as_public(self) -> Any:
        raise NotImplementedError

    def can_encrypt(self) -> bool:
        """Return a boolean indicating if this implementation can encrypt
        data.
        """
        raise NotImplementedError

    def can_sign(self) -> bool:
        """Return a boolean indicating if this implementation can create
        a digital signature.
        """
        raise NotImplementedError

    def can_perform(self, op: str | KeyOperationType) -> bool:
        """Return a boolean indicating if the key can perform the
        given cryptographic operation.
        """
        raise NotImplementedError

    def can_verify(self) -> bool:
        """Return a boolean indicating if this implementation can verify
        a digital signature.
        """
        raise NotImplementedError

    def has_key_material(self) -> bool:
        """Return a boolean indicating if the key material"""
        raise NotImplementedError

    def is_asymmetric(self) -> bool:
        """Return a boolean indicating if the key is an asymmetric
        algorithm.
        """
        raise NotImplementedError

    def is_loaded(self) -> bool: # pragma: no cover
        """Return a boolean indicating if the metadata describing the
        key is retrieved.
        """
        raise NotImplementedError

    def is_public(self) -> bool:
        """Return a boolean indicating if this specification represent
        a public key.
        """
        raise NotImplementedError