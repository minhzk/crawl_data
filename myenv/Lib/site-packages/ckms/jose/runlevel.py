# Copyright 2018 Cochise Ruhulessin
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

from unimatrix.conf import settings # type: ignore

from .trustedissuers import TrustedIssuers


TRUSTED_ISSUERS: dict[str, Any] = getattr(
    settings, 'TRUSTED_ISSUERS', [] # type: ignore
)


async def init():
    """Loads the preconfigured issuers in the default store."""
    trust = TrustedIssuers.default()
    for issuer in TRUSTED_ISSUERS:
        trust.trust(issuer=issuer)
    await trust