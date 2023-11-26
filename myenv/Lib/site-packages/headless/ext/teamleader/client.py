# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

from headless.core.httpx import Client
from headless.types import IResource


M = TypeVar('M', bound=IResource)


class TeamleaderClient(Client):
    __module__: str = 'headless.ext.teamleader'

    async def retrieve(
        self,
        model: type[M],
        resource_id: int | str | None = None
    ) -> M:
        meta = model.get_meta()
        response = await self.post(
            url=model.get_retrieve_url(resource_id),
            json={'id': str(resource_id)},
            headers=meta.headers
        )
        response.raise_for_status()
        self.check_json(response.headers)
        data = self.process_response('retrieve', await response.json())
        return self.resource_factory(model, 'retrieve', data)