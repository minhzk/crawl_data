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
import copy
import json
import types
from typing import Any

import pytest

from ckms.core import Keychain
from ckms.core.const import ENCRYPTION_ALGORITHMS
from ckms.core.models import KeySpecification
from ckms.jose.decoder import Decoder
from ckms.jose.encoder import Encoder
from ckms.utils import b64encode_json
from .josebasetestcase import JOSEBaseTestCase


TEST_PAYLOADS: list[bytes | dict[str, Any]] = [
    b'Hello world!',
    str.encode(json.dumps({'foo': 'bar'}), 'utf-8')
]


class JOSEEncryptionTestCase(JOSEBaseTestCase):
    __module__: str = 'ckms.core.provider.tests'
    supported_encryption_algorithms: set[str] = set(ENCRYPTION_ALGORITHMS)
    supported_wrapping_algorithms: set[str] = set()
    tests_package: types.ModuleType | None = None

    async def create_jwe(
        self,
        *,
        encoder: Encoder,
        recipients: list[tuple[KeySpecification, dict[str, Any] | None]],
        recipient: KeySpecification |  None = None,
        payload: bytes | dict[str, Any],
        signers: list[Any] | None = None,
        expect_jwt: bool = False,
        compact: bool = False,
        direct: bool = False
    ) -> str:
        signers = signers or []
        obj = encoder.encode(content=payload)
        for spec, protected, header in signers:
            obj.add_signature(signer=spec, protected=protected, header=header)
        for spec, header in recipients:
            obj.add_recipient(encrypter=spec, header=header, direct=direct)
        return await obj.serialize(compact=compact)

    async def decrypt_jwe(
        self,
        encoder: Encoder,
        decoder: Decoder,
        recipients: list[tuple[KeySpecification, dict[str, Any] | None]],
        signers: list[list[Any]],
        payload: bytes | dict[str, Any],
        token: str
    ) -> Any:
        return await decoder.decode(token)

    @pytest.mark.parametrize("name", ["RSA-OAEP"])
    @pytest.mark.parametrize("encryption", ["A256GCM"])
    @pytest.mark.parametrize("payload", [
        b'Hello world!',
        {'foo': 'bar'}
    ])
    @pytest.mark.parametrize("header", [
        None,
        {'foo': 'bar'}
    ])
    @pytest.mark.parametrize("compact", [True, False])
    @pytest.mark.parametrize("signers", [
        None,
        [('HS256', None, None)],
        [('HS256', None, None), ('HS384', None, None)],
    ])
    @pytest.mark.asyncio
    async def test_wrap_single(
        self,
        encoder: Encoder,
        decoder: Decoder,
        keychain: Keychain,
        name: str,
        encryption: str | None,
        payload: bytes | dict[str, Any],
        header: dict[str, Any] | None,
        compact: bool,
        signers: list[list[Any]],
        direct: bool = False,
        recipients: list[tuple[KeySpecification, dict[str, Any] | None]] | None = None
    ):
        is_jwt = isinstance(payload, dict)
        payload = copy.deepcopy(payload)
        signers = copy.deepcopy(list(signers or []))
        if not recipients:
            spec: KeySpecification = keychain.get(name)
            if direct and not spec.can_encrypt():
                pytest.skip()
            elif not direct and not spec.can_wrap():
                pytest.skip()
            elif not direct and spec.algorithm\
            not in self.supported_wrapping_algorithms:
                pytest.skip()
            recipients = [
                (spec, header)
            ]
    
        for i, signer in enumerate(signers):
            signer_name, *headers = signer
            signers[i] = [keychain.get(signer_name)] + headers

        compact = compact and (len(recipients) <= 1 and len(signers) <= 1)
        token = await self.create_jwe(
            encoder=encoder,
            recipients=recipients,
            payload=payload,
            compact=compact,
            direct=direct,
            signers=signers
        )
        if isinstance(token, dict):
            token = bytes.decode(b64encode_json(token), 'ascii')
        await self.decrypt_jwe(
            encoder=encoder,
            decoder=decoder,
            recipients=recipients,
            signers=signers,
            payload=payload,
            token=token
        )

        headers, _ = decoder.introspect(token)
        typ = "JOSE" if compact else "JOSE+JSON"
        cty = "application/octet-stream"
        if recipients and signers:
            cty = "JOSE" if compact else "JOSE+JSON"
        if is_jwt:
            cty = None
            typ = "JWT"
            if signers:
                cty = "JWT"
        for i, jose in enumerate(headers):
            assert jose.alg in {recipients[i][0].algorithm, 'dir'}
            assert jose.kid == recipients[i][0].kid
            assert jose.typ == typ
            assert jose.cty == cty, jose

    @pytest.mark.parametrize("recipient1", [
        ('A128GCMKW', None),
        ('A128GCMKW', {'foo': 'bar'}),
    ])
    @pytest.mark.parametrize("recipient2", [
        ('A192GCMKW', None),
        ('A192GCMKW', {'foo': 'bar'}),
    ])
    @pytest.mark.parametrize("encryption", sorted(ENCRYPTION_ALGORITHMS))
    @pytest.mark.parametrize("payload", [
        b'Hello world!',
        str.encode(json.dumps({'foo': 'bar'}), 'utf-8')
    ])
    @pytest.mark.asyncio
    async def test_wrap_multi(
        self,
        encoder: Encoder,
        decoder: Decoder,
        keychain: Keychain,
        recipient1: tuple[str, dict[str, Any] | None],
        recipient2: tuple[str, dict[str, Any] | None],
        encryption: str,
        payload: bytes
    ):
        recipients = [
            (keychain.get(recipient1[0]), recipient1[1]),
            (keychain.get(recipient2[0]), recipient2[1]),
        ]
        await self.test_wrap_single(
            encoder=encoder,
            decoder=decoder,
            keychain=keychain,
            name='',
            encryption=encryption,
            payload=payload,
            header={},
            compact=False,
            recipients=recipients,
            signers=[]
        )

    @pytest.mark.parametrize("compact", [True, False])
    @pytest.mark.parametrize("header", [
        None,
        {'foo': 'bar'}
    ])
    @pytest.mark.parametrize("name", sorted(ENCRYPTION_ALGORITHMS))
    @pytest.mark.parametrize("payload", [
        b'Hello world!',
        str.encode(json.dumps({'foo': 'bar'}), 'utf-8')
    ])
    @pytest.mark.asyncio
    async def test_direct_single(
        self,
        encoder: Encoder,
        decoder: Decoder,
        keychain: Keychain,
        name: str,
        payload: bytes | dict[str, Any],
        header: dict[str, Any] | None,
        compact: bool
    ):
        await self.test_wrap_single(
            encoder=encoder,
            decoder=decoder,
            keychain=keychain,
            name=name,
            encryption=None,
            payload=payload,
            header=header,
            compact=compact,
            direct=True,
            signers=[]
        )