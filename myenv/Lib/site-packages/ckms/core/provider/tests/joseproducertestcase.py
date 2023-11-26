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
import json
from typing import Any

import pytest

from ckms.core import Keychain
from ckms.core import KeyInspector
from ckms.core.models import KeySpecification
from ckms.utils import b64encode
from ckms.jose.encoder import Encoder


class JOSEProducerTestCase:
    __module__: str = 'ckms.jose.tests'
    inspector: KeyInspector = KeyInspector()
    supports_compact: bool = True
    supports_flattened: bool = True
    supports_json: bool = True
    supports_multi: bool = True

    def get_data(self) -> Any:
        return "Hello world!"

    def jwk_from_spec(self, spec: KeySpecification) -> dict[str, Any]:
        k: dict[str, Any]
        if spec.is_symmetric():
            k = dict(
                kty='oct',
                k=b64encode(spec.get_key_material()).decode('ascii')
            )
        else:
            k = dict(**spec.as_jwk().dict(exclude_defaults=True))
        return k

    async def create_jws(
        self,
        encoder: Encoder,
        signers: list[tuple[KeySpecification, Any, Any]],
        payload: bytes | dict[str, Any],
        compact: bool = False,
    ) -> Any:
        obj = encoder.encode(content=payload)
        for signer, protected, header in signers:
            assert not protected
            obj.add_signature(
                signer=signer,
                protected=protected,
                header=header
            )
        return await obj.serialize(compact=compact)

    async def verify_jws(
        self,
        verifiers: list[KeySpecification],
        token: bytes,
        payload: str | None = None,
        expect_jwt: bool = False
    ) -> None:
        raise NotImplementedError

    @pytest.mark.parametrize("compact", [False, True])
    @pytest.mark.parametrize("data", [None, {'foo': 'bar'}])
    async def test_sign_single_jws(
        self,
        keychain: Keychain,
        name: str,
        encoder: Encoder,
        compact: bool,
        data: Any
    ):
        """Encode a JWS with a single signature."""
        if compact and not self.supports_compact:
            pytest.skip()
        if not compact and not (self.supports_flattened or self.supports_multi):
            pytest.skip()
        spec = keychain.get(name)
        assert await self.verify_jws(
            verifiers=[spec],
            token=await self.create_jws(
                encoder=encoder,
                payload=data or self.get_data(),
                signers=[(spec, None, None)],
                compact=compact
            ),
            payload=json.dumps(data) if data else self.get_data(),
            expect_jwt=isinstance(data, dict)
        )

    async def test_sign_single_jws_different_key_does_not_verify(
        self,
        keychain: Keychain,
        name: str,
        hs256: KeySpecification,
        encoder: Encoder
    ):
        """Encode a JWS with a single signature."""
        spec = keychain.get(name)
        assert not await self.verify_jws(
            verifiers=[hs256],
            token=await self.create_jws(
                encoder=encoder,
                payload=self.get_data(),
                signers=[(spec, None, None)],
                compact=True
            ),
            payload=self.get_data()
        )

    @pytest.mark.parametrize("data", [None, {'foo': 'bar'}])
    async def test_sign_multi_jws(
        self,
        keychain: Keychain,
        name: str,
        hs256: KeySpecification,
        encoder: Encoder,
        data: Any
    ):
        if not self.supports_multi:
            pytest.skip()
        spec = keychain.get(name)
        assert await self.verify_jws(
            verifiers=[spec, hs256],
            token=await self.create_jws(
                encoder=encoder,
                payload=data or self.get_data(),
                signers=[
                    (spec, None, None),
                    (hs256, None, None)
                ],
                compact=False
            ),
            payload=json.dumps(data) if data else self.get_data()
        )

    async def test_sign_multi_jws_different_key_does_not_verify(
        self,
        keychain: Keychain,
        name: str,
        hs256: KeySpecification,
        hs384: KeySpecification,
        encoder: Encoder
    ):
        if not self.supports_multi:
            pytest.skip()
        spec = keychain.get(name)
        assert not await self.verify_jws(
            verifiers=[hs384],
            token=await self.create_jws(
                encoder=encoder,
                payload=self.get_data(),
                signers=[
                    (spec, None, None),
                    (hs256, None, None)
                ],
                compact=False
            ),
            payload=self.get_data()
        )