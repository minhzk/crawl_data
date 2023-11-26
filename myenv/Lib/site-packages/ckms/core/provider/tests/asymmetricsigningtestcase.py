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
import pytest

from ckms.types import Message
from ckms.core.models import KeySpecification
from .baseprovidertestcase import BaseProviderTestCase


class AsymmetricSigningTestCase(BaseProviderTestCase):

    @pytest.mark.asyncio
    async def test_spec_to_jwk(self, spec: KeySpecification):
        await spec
        jwk = spec.as_jwk()
        assert jwk.kty == spec.kty
        assert jwk.alg == spec.algorithm

    @pytest.mark.asyncio
    async def test_verify_from_jwk(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        await spec
        jwk = spec.as_jwk(private=False)
        sig = await self.sign(spec, data)
        await self.verify(jwk, sig, data)

    @pytest.mark.asyncio
    async def test_sign_bytes(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.can_sign():
            pytest.skip()
        await self.sign(spec, data)

    @pytest.mark.asyncio
    async def test_sign_message(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.can_sign():
            pytest.skip()
        await self.sign(spec, Message(buf=data))

    @pytest.mark.asyncio
    async def test_verify_message(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.can_sign():
            pytest.skip()
        sig = await self.sign(spec, Message(buf=data))
        assert await self.verify(spec.as_public(), sig, Message(buf=data))

    @pytest.mark.asyncio
    async def test_asymmetric_verify_from_provider(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.is_asymmetric() or not spec.can_sign():
            pytest.skip()
        sig = await self.sign(spec, data)
        assert await self.verify(spec.as_public(), sig, data)

    @pytest.mark.asyncio
    async def test_asymmetric_verify_from_provider_invalid(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.is_asymmetric() or not spec.can_sign():
            pytest.skip()
        sig = await self.sign(spec, data)
        assert not await self.verify(spec.as_public(), sig, b'foo')

    @pytest.mark.asyncio
    async def test_asymmetric_verify_from_provider_signature_too_short(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.is_asymmetric() or not spec.can_sign():
            pytest.skip()
        sig = await self.sign(spec, data)
        assert not await self.verify(spec.as_public(), sig[:-1], data)

    @pytest.mark.asyncio
    async def test_asymmetric_verify_from_provider_signature_too_long(
        self,
        spec: KeySpecification,
        data: bytes
    ) -> None:
        if not spec.is_asymmetric() or not spec.can_sign():
            pytest.skip()
        sig = await self.sign(spec, data)
        assert not await self.verify(spec.as_public(), sig + b'0', data)