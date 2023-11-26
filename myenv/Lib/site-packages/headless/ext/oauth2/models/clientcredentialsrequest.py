# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Iterable
from typing import Literal

import pydantic

from headless.types import IClient
from .iobtainable import IObtainable
from .tokenresponse import TokenResponse
from .servermetadata import ServerMetadata


class ClientCredentialsRequest(IObtainable, pydantic.BaseModel):
    grant_type: Literal['client_credentials'] = 'client_credentials'
    scope: str

    @pydantic.validator('scope', pre=True)
    def preprocess_scope(
        cls,
        value: Iterable[str] | str
    ) -> str:
        if not isinstance(value, str):
            value = ' '.join(sorted(value))
        return value

    async def obtain(
        self,
        client: IClient[Any, Any],
        metadata: ServerMetadata
    ) -> TokenResponse:
        if metadata.token_endpoint is None:
            raise NotImplementedError
        response = await client.post(
            url=metadata.token_endpoint,
            json=self.dict()
        )
        response.raise_for_status()
        return TokenResponse.parse_obj(await response.json())