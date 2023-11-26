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

from ckms.jose import PayloadCodec
from ckms.core import Keychain
from ckms.core.models import KeySpecification
from ckms.types import InvalidSignature
from .conftest import SIGNING_KEYS_ASYMMETRIC
from .conftest import SIGNING_KEYS_SYMMETRIC



@pytest.mark.parametrize("spec", [
    *SIGNING_KEYS_ASYMMETRIC,
    *SIGNING_KEYS_SYMMETRIC
])
class TestProviderJWS:

    @pytest.mark.asyncio
    async def test_sign_and_verify_compact(
        self,
        signer: Keychain,
        verifier: Keychain,
        spec: KeySpecification
    ):
        assert spec.kid is not None
        c1 = PayloadCodec(
            signer=signer,
            verifier=verifier,
            signing_keys=[spec.kid]
        )
        c2 = PayloadCodec()
        jws = await c1.encode({'foo': 1})
        assert await c1.decode(jws, verify=True)
        with pytest.raises(InvalidSignature):
            await c2.decode(jws, verify=True)