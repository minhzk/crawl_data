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
import os

import pytest

from ckms.core.models import KeySpecification
from ckms.types import CipherText
from .baseprovidertestcase import BaseProviderTestCase


class EncryptionTestCase(BaseProviderTestCase):
    __module__: str = 'ckms.core.types.provider.tests'

    @pytest.mark.asyncio
    async def test_encrypt_bytes(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        ct = await self.encrypt(spec, data)
        assert isinstance(ct, CipherText)

    @pytest.mark.asyncio
    async def test_decrypt_bytes(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        ct = await self.encrypt(spec, data)
        assert isinstance(ct, CipherText)
        assert await self.decrypt(spec, ct) == data

    @pytest.mark.asyncio
    async def test_decrypt_bytes_with_aad(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        if not spec.is_aead():
            pytest.skip()
        aad = b'foo'
        ct = await self.encrypt(spec, data, aad=aad)
        assert isinstance(ct, CipherText)
        assert ct.aad == aad, ct.aad
        assert await self.decrypt(spec, ct) == data

    @pytest.mark.asyncio
    async def test_decrypt_bytes_with_missing_aad_raises_exception(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        if not spec.is_aead():
            pytest.skip()
        aad = b'foo'
        ct = await self.encrypt(spec, data, aad=aad)
        assert isinstance(ct, CipherText)
        assert ct.aad == aad, ct.aad
        ct.aad = None
        try:
            assert await self.decrypt(spec, ct) == data
        except self.provider.Undecryptable:
            pass

    @pytest.mark.asyncio
    async def test_decrypt_bytes_with_different_aad_raises_exception(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        if not spec.is_aead():
            pytest.skip()
        aad = b'foo'
        ct = await self.encrypt(spec, data, aad=aad)
        assert isinstance(ct, CipherText)
        assert ct.aad == aad, ct.aad
        ct.aad = b'bar'
        try:
            assert await self.decrypt(spec, ct) == data
        except self.provider.Undecryptable:
            pass

    @pytest.mark.asyncio
    async def test_decrypt_bytes_with_missing_iv_raises_exception(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        if not spec.is_symmetric():
            pytest.skip()
        ct = await self.encrypt(spec, data)
        assert isinstance(ct, CipherText)
        ct.iv = None
        try:
            await self.decrypt(spec, ct)
        except self.provider.Undecryptable:
            pass

    @pytest.mark.asyncio
    async def test_decrypt_bytes_with_different_iv_raises_exception(
        self,
        spec: KeySpecification,
        data: bytes
    ):
        if not spec.is_asymmetric():
            pytest.skip()
        ct = await self.encrypt(spec, data)
        assert isinstance(ct, CipherText)
        ct.iv = os.urandom(12)
        try:
            assert await self.decrypt(spec, ct) == data
        except self.provider.Undecryptable:
            pass