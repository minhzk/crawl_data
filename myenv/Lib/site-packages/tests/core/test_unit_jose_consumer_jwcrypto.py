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
from typing import cast
from typing import Any

import pytest
from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS

from ckms.core.models import KeySpecification
from ckms.core.provider.tests import JOSEConsumerTestCase
from ckms.utils import b64encode


class TestConsumeJOSE(JOSEConsumerTestCase):

    def create_jws(
        self,
        signers: list[tuple[KeySpecification, dict[str, Any] | None, dict[str, Any] | None]],
        claims: dict[str, Any] | None = None,
        compact: bool = False,
        encode: bool = False
    ) -> bytes:
        """Create a JSON Web Signature (JWS) using the given claims."""
        jws = JWS(self.payload)
        for spec, protected, header in signers:
            assert spec.algorithm is not None
            if spec.algorithm not in jws.allowed_algs: # type: ignore
                if len(signers) <= 1:
                    pytest.skip()
                continue
            key = JWK(**spec.as_jwk(private=True).dict(exclude_defaults=True))
            if compact:
                # Compact encoding must carry 'alg' in protected header
                protected = protected or {}
                protected.setdefault('alg', spec.algorithm)
            jws.add_signature( # type: ignore
                key=key,
                alg=spec.algorithm,
                protected=protected,
                header=header
            )

        buf = str.encode(cast(str, jws.serialize(compact=compact)), 'utf-8')
        if encode and not compact:
            buf = b64encode(buf)
        return buf