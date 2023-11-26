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
"""Declares :class:`Signature`."""
import inspect
from typing import cast
from typing import Any

import pydantic

from ckms.core.exceptions import MissingProtectedClaim
from ckms.core.exceptions import MissingProtectedHeader
from ckms.types import IKeychain
from ckms.types import Verifier
from ckms.utils import b64decode
from .joseheader_ import JOSEHeader


class Signature(pydantic.BaseModel):
    protected: str
    header: JOSEHeader = pydantic.Field(
        default_factory=JOSEHeader,
        exclude=True
    )
    signature: str

    @property
    def alg(self) -> str | None:
        return self.header.alg

    @property
    def kid(self) -> str | None:
        return self.header.kid

    @pydantic.root_validator(allow_reuse=True, pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        protected = values.get('protected')
        if not protected:
            raise MissingProtectedHeader
        return values

    def json(self, **kwargs: Any) -> dict[str, Any]: # type: ignore
        kwargs.setdefault('exclude', ['header'])
        return super().dict(**kwargs)

    def dict(self, **kwargs: Any) -> dict[str, Any]: # type: ignore
        kwargs.setdefault('exclude', ['header'])
        return super().dict(**kwargs)

    async def verify(
        self,
        keychain: IKeychain,
        payload: str,
        require_kid: bool = True
    ) -> bool:
        """Verifies that this signature was created for the given payload using the
        given `keychain`.
        
        The `require_kid` indicates if the ``kid`` is required to be present on in
        the JOSE header. If `require_kid` is ``True`` and the claim is not present,
        validation fails immediately. Otherwise, all keys in the `keychain` are
        attempted to verify the signature with the specified algorithm.
        """
        if not self.kid and require_kid:
            raise MissingProtectedClaim('kid')
        if not self.alg:
            raise MissingProtectedClaim('alg')
        result = False

        # Construct the signing input and decode the signature
        signing_input = str.encode('.'.join([self.protected, payload]), 'ascii')
        signature = b64decode(self.signature)

        # Use the key identifier to lookup the key. If not present, resort to
        # all registered keys with the given algorithm.
        if self.kid and keychain.has(self.kid):
            spec = cast(Verifier, keychain.get(kid=self.kid))
            if spec.allows_algorithm(self.alg):
                result = spec.verify(
                    signature=signature,
                    message=signing_input
                )
                if inspect.isawaitable(result):
                    result = await result
        elif not require_kid:
            keychain = keychain.filter(
                algorithm=self.alg,
                kid=self.kid,
                use='sig',
                op='verify'
            )
            for spec in keychain.verifiers():
                if not spec.allows_algorithm(self.alg):
                    continue
                result = spec.verify(
                    signature=signature,
                    message=signing_input
                )
                if inspect.isawaitable(result):
                    result = await result
                if result:
                    break
            else:
                result = False
        return result

    def __eq__(self, y: 'Signature') -> bool:
        return self.signature == y.signature
