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
from typing import Any

from ckms.core.models import KeySpecification
from ckms.utils import b64encode


class JOSEBaseTestCase:
    __module__: str = 'ckms.core.providers.tests'
    supports_compact: bool = True
    supports_flattened: bool = True
    supports_json: bool = True
    supports_multi: bool = True

    def jwk_from_spec(self, spec: KeySpecification, private: bool = False) -> dict[str, Any]:
        k: dict[str, Any]
        if spec.is_symmetric():
            k = dict(
                kty='oct',
                kid=spec.kid,
                k=b64encode(spec.get_key_material()).decode('ascii')
            )
        else:
            k = dict(**spec.as_jwk(private=private).dict(exclude_defaults=True))
        return k