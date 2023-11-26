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
import copy
import json
from typing import Any

import pytest
from jwcrypto.jwe import default_allowed_algs as default_jwe_algs
from jwcrypto.jwe import JWE
from jwcrypto.jwk import JWK
from jwcrypto.jws import default_allowed_algs as default_jws_algs
from jwcrypto.jws import JWS
from jwcrypto.jws import InvalidJWSSignature

from ckms.core.const import SIGNING_ALGORITHMS
from ckms.core.models import KeySpecification
from ckms.core.provider.tests import JOSEProducerTestCase
from ckms.core.provider.tests import JOSEEncryptionTestCase
from ckms.jose.decoder import Decoder
from ckms.jose.encoder import Encoder
from ckms.utils import b64encode


ENCRYPTION_ALGORITHMS: list[str] = list(
    sorted(set(default_jwe_algs) - {'dir'})
)


class TestEncryptionCompatibility(JOSEEncryptionTestCase):
    supported_wrapping_algorithms: set[str] = set(ENCRYPTION_ALGORITHMS)

    def jwk_from_spec(
        self,
        spec: KeySpecification,
        private: bool = False
    ) -> dict[str, Any]:
        return super().jwk_from_spec(spec, True)

    async def decrypt_jwe(
        self,
        encoder: Encoder,
        decoder: Decoder,
        recipients: list[tuple[KeySpecification, dict[str, Any] | None]],
        signers: list[tuple[KeySpecification, dict[str, Any] | None, dict[str, Any] | None]],
        payload: bytes | dict[str, Any],
        token: str | dict[str, Any]
    ) -> Any:
        jwe = JWE()
        jwe.deserialize(token)
        for spec, header in recipients:
            jwk = JWK(**self.jwk_from_spec(spec))
            jwe.decrypt(jwk)
            break
        return jwe.payload


@pytest.mark.parametrize("name", default_jws_algs)
class TestDeserializeCompatibility(JOSEProducerTestCase):

    async def verify_jws(
        self,
        verifiers: KeySpecification,
        token: bytes,
        payload: str | None = None,
        expect_jwt: bool = False
    ):
        jws = self.deserialize_jws(token)
        if payload is not None:
            assert jws.objects.get('payload') == str.encode(payload, 'utf-8')
        verified = False
        for spec in verifiers:
            k = JWK(**self.jwk_from_spec(spec))
            try:
                jws.verify(k)
            except InvalidJWSSignature:
                break
        else:
            verified = True
        return verified

    def deserialize_jws(self, token: str) -> JWS:
        jws = JWS()
        jws.deserialize(token) # type: ignore
        return jws