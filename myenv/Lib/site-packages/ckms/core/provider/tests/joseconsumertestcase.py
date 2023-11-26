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
import enum
from typing import cast
from typing import Any

import pytest
from jwcrypto.common import json_encode # type: ignore

from ckms.core import const
from ckms.core import Keychain
from ckms.core.exceptions import MissingProtectedClaim
from ckms.core.models import JOSEObject
from ckms.core.models import JSONWebSignature
from ckms.core.models import KeySpecification
from .baseprovidertestcase import BaseProviderTestCase



class JOSELibraryCapability(str, enum.Enum):
    multisign = 'multisign'


class JOSEConsumerTestCase(BaseProviderTestCase):
    name: str = 'local'
    payload: bytes = b'Hello world!'
    capabilities: set[str] = set()
    Capability: type[enum.Enum] = JOSELibraryCapability

    def create_jws(
        self,
        signers: list[tuple[KeySpecification, dict[str, Any] | None, dict[str, Any] | None]],
        claims: dict[str, Any] | None = None,
        compact: bool = False,
        encode: bool = False
    ) -> bytes:
        """Create a JSON Web Signature (JWS) using the given claims."""
        raise NotImplementedError

    @pytest.mark.parametrize("algorithm", const.SIGNING_ALGORITHMS)
    @pytest.mark.parametrize("compact", [True, False])
    @pytest.mark.parametrize("encode", [True, False])
    @pytest.mark.parametrize("require_kid", [True, False])
    @pytest.mark.parametrize("protected", [
        {'foo': 1},
    ])
    @pytest.mark.parametrize("header", [
        None,
        {'bar': 1}
    ])
    @pytest.mark.asyncio
    async def test_sign_and_verify_jws_single(
        self,
        algorithm: str,
        keychain: Keychain,
        protected: dict[str, Any] | None,
        header: dict[str, Any] | None,
        compact: bool,
        encode: bool,
        require_kid: bool
    ):
        if header is not None:
            header = copy.deepcopy(header)
        spec = keychain.get(algorithm)
        protected = copy.deepcopy(protected or {})
        protected.setdefault('alg', spec.algorithm)
        assert spec.kid is not None
        if require_kid:
            header = header or {}
            header.setdefault('kid', spec.kid)
        if compact:
            protected = protected or {}
            protected.update(header or {})
            header = None

        buf = self.create_jws(
            signers=[
                (spec, protected, header)
            ],
            compact=compact,
            encode=encode
        )
        jws = cast(JSONWebSignature, JOSEObject.parse(buf))

        assert isinstance(jws, JSONWebSignature)
        success = await jws.verify(keychain, require_kid=require_kid)
        if protected.get('alg') != spec.algorithm:
            assert not success
        else:
            assert success

    @pytest.mark.parametrize("algorithm", const.SIGNING_ALGORITHMS)
    @pytest.mark.asyncio
    async def test_sign_with_missing_kid_never_validates(
        self,
        algorithm: str,
        keychain: Keychain    
    ):
        spec = keychain.get(algorithm)
        buf = self.create_jws(
            signers=[
                (spec, {'alg': spec.algorithm}, None)
            ]
        )
        jws = cast(JSONWebSignature, JOSEObject.parse(buf))
        try:
            assert not await jws.verify(keychain, require_kid=True)
        except MissingProtectedClaim as exception:
            assert exception.claim == 'kid'

    @pytest.mark.parametrize("algorithm", const.SIGNING_ALGORITHMS)
    @pytest.mark.asyncio
    async def test_sign_with_missing_kid_validates_if_require_kid_is_false(
        self,
        algorithm: str,
        keychain: Keychain    
    ):
        spec = keychain.get(algorithm)
        buf = self.create_jws(
            signers=[
                (spec, {'alg': spec.algorithm}, None)
            ]
        )
        jws = cast(JSONWebSignature, JOSEObject.parse(buf))
        assert await jws.verify(keychain, require_kid=False)