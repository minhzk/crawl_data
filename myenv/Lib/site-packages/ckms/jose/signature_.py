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
"""Declares :class:`Signature`."""
import json

from typing import Any

from ckms.types import Data
from ckms.types import Signer
from ckms.utils import b64encode


class Signature:
    __module__: str = 'ckms.jose'
    header: dict[str, Any]
    payload: Data
    protected: dict[str, Any]
    protected_b64: bytes | None = None
    signer: Signer
    signature: bytes | None = None

    def __init__(
        self,
        *,
        protected: dict[str, Any],
        signer: Signer,
        payload: Data,
        header: dict[str, Any] | None = None
    ):
        self.header = header or {}
        self.payload = payload
        self.protected = protected
        self.signer = signer

        protected.update({
            'alg': signer.algorithm
        })

    async def sign(
        self,
        payload: bytes,
        protected: dict[str, Any] | None = None,
        compact: bool = False
    ) -> 'Signature':
        """Create a signature of the protected header and the payload using the
        signing key supplied at initialization.
        """
        protected = {**(protected or {}), **self.protected}
        if compact and self.header:
            protected = {**self.header, **protected}
        if self.signature is None:
            self.protected_b64 = b64encode(
                json.dumps(protected, sort_keys=True).encode('utf-8')
            )
            message = b'.'.join([self.protected_b64, payload])
            self.signature = b64encode(await self.signer.sign(message))
            assert bool(self)
        return self

    def dict(self, compact: bool) -> dict[str, Any]:
        """Dump the JSON Web Signature (JWS) using the JWS JSON Serialization
        schema.
        """
        assert self.protected_b64 is not None
        if self.signature is None:
            raise ValueError("Invoke Signature.sign() before serializing.")
        jws: dict[str, Any] = {
            'protected': bytes.decode(self.protected_b64, 'ascii'),
            'signature': bytes.decode(self.signature, 'ascii')
        }
        if not compact and bool(self.header):
            jws['header'] = self.header
        return jws

    def __bool__(self) -> bool:
        return bool(self.signature)

    def __repr__(self) -> str:
        return f'<Signarure: signed={bool(self)}>'