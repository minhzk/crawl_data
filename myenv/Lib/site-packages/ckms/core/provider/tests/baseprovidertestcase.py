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
import inspect
from typing import Any

import pytest

import ckms.core
from ckms.core.models import KeySpecification
from ckms.types import CipherText
from ckms.types import Message
from ckms.types import IProvider
from ckms.types import Verifier


class BaseProviderTestCase:
    name: str

    @property
    def provider(self) -> IProvider:
        """The :class:`~ckms.core.types.IProvider` implementation that
        is being tested.
        """
        return self.get_provider()

    @classmethod
    def setup_class(cls) -> None:
        pass

    def get_provider(self) -> IProvider:
        """Returns the :class:`~ckms.core.types.IProvider` instance that
        is being tested.
        """
        return ckms.core.provider(self.name)

    async def decrypt(
        self,
        spec: KeySpecification,
        ct: CipherText
    ) -> bytes:
        await spec
        pt = spec.decrypt(ct, force=True)
        if inspect.isawaitable(pt):
            pt = await pt
        return pt

    async def encrypt(
        self,
        spec: KeySpecification,
        pt: bytes,
        **kwargs: Any
    ) -> CipherText:
        await spec
        kwargs.setdefault('force', True)
        ct = spec.encrypt(pt, **kwargs)
        if inspect.isawaitable(ct):
            ct = await ct
        return ct

    async def sign(
        self,
        spec: KeySpecification,
        data: bytes | Message
    ) -> bytes:
        await spec
        sig = spec.sign(data)
        if inspect.isawaitable(sig):
            sig = await sig
        return sig

    async def verify(
        self,
        spec: Verifier,
        sig: bytes,
        data: bytes | Message
    ) -> bool:
        result = spec.verify(sig, data)
        if inspect.isawaitable(result):
            result = await result
        return result