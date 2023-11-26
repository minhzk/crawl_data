# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from .bearertokencredential import BearerTokenCredential


class TokenResponse(pydantic.BaseModel):
    token_type: Literal['Bearer']
    expires_in: int
    access_token: BearerTokenCredential
    refresh_token: str | None = None
    id_token: str | None = None