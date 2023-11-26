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
"""Declares :class:`Encoder`."""
from typing import cast
from typing import Any

from ckms.types import ClaimSet
from ckms.types import Data
from ckms.types import IKeychain
from ckms.types import IKeySpecification
from ckms.types import Encrypter
from ckms.types import Signer
from .josepayload import JOSEPayload


class Encoder:
    """Provides an interface to create JOSE objects."""
    __module__: str = 'ckms.jose'
    allow_compact: bool
    allow_flattened: bool
    encrypter: IKeychain
    encryption_keys: list[str]
    signer: IKeychain
    signing_keys: list[str | Signer]

    def __init__(
        self,
        *,
        encrypter: IKeychain,
        signer: IKeychain,
        encryption_keys: list[str | IKeySpecification] | None = None,
        signing_keys: list[str | IKeySpecification] | None = None,
        allow_compact: bool = True,
        allow_flattened: bool = True
    ) -> None:
        self.allow_compact = allow_compact
        self.allow_flattened = allow_flattened
        self.encrypter = encrypter
        self.encryption_keys = encryption_keys or []
        self.signer = signer
        self.signing_keys = signing_keys or []

    def encode(
        self,
        content: bytes | dict[str, Any] | str | ClaimSet | Data,
        sign: bool = True,
        encrypt: bool = True,
        content_type: str | None = None,
        claimset_class: type[ClaimSet] = ClaimSet,
        signing_keys: list[str] | None = None,
        signers: list[IKeySpecification] | list[Signer] | list[str] | None = None,
        encrypters: list[str] | list[Encrypter] | None = None,
        allow_compact: bool = True,
        allow_flattened: bool = True
    ) -> JOSEPayload:
        """Encode claim set or readable byte-sequence `content` using the
        :class:`~ckms.types.IKeychain` supplied at intialziation.
        
        If `content` is a dictionary, assume that it is a JWT claims set. Otherwise,
        `content` is :class:`ckms.types.ClaimSet` or :class:`ckms.types.Data`. In the
        latter case, the instance *must* set the :attr:`~ckms.types.Data.content_type`
        attribute.

        For the case that a JWT claims set is being encoded but its content type
        is not ``JWT``, the `content_type` parameter may be supplied to override
        the default content type, for example when encoding an :rfc:`RFC9068`
        access token which uses ``at+jwt`` as its content type.
        """
        encrypters = encrypters or self.encryption_keys
        must_encrypt = encrypt and bool(encrypters)
        must_sign = sign or bool(signing_keys) or bool(signers)
        signers = signers or signing_keys or self.signing_keys
        if isinstance(content, str):
            content = str.encode(content, 'utf-8')
        if isinstance(content, bytes):
            content = Data(buf=content, content_type="application/octet-stream")
        if isinstance(content, dict):
            content = claimset_class(**content)
        obj = JOSEPayload(
            payload=content,
            content_type=content_type,
            allow_compact=self.allow_compact or allow_compact,
            allow_flattened=self.allow_flattened or allow_flattened
        )
        if must_sign:
            for signer in signers:
                if isinstance(signer, str):
                    signer = cast(Signer, self.signer.get(signer))
                self._sign_jws(obj, signer)
        if must_encrypt:
            for encrypter in encrypters:
                if isinstance(encrypter, str):
                    encrypter = cast(Encrypter, self.encrypter.get(encrypter))
                obj.add_recipient(
                    encrypter=encrypter,
                    direct=encrypter.can_encrypt()
                )
                
        return obj

    def _sign_jws(self, obj: JOSEPayload, signer: Signer) -> None:
        assert self.signer is not None
        obj.add_signature(
            signer=signer,
            protected={'alg': signer.algorithm, 'kid': signer.kid}
        )