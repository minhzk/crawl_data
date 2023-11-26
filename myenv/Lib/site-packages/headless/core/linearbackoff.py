# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
from typing import Any

from headless.types import IBackoff
from headless.types import IClient
from headless.types import IRequest
from headless.types import IResponse


class LinearBackoff(IBackoff):
    __module__: str = 'headless.core'
    interval: int
    max_delay: int = 300
    max_retries: int

    def __init__(self, interval: int, max_retries: int):
        self.interval = interval
        self.max_retries = max_retries

    def parse_retry_after(self, response: IResponse[Any, Any]) -> int:
        if not response.headers.get('Retry-After'):
            return self.interval
        try:
            retry_after = int(response.headers['Retry-After'])
        except (TypeError, ValueError):
            retry_after = self.interval
        return min(self.max_delay, retry_after)

    async def retry(
        self,
        client: IClient[Any, Any],
        request: IRequest[Any],
        response: IResponse[Any, Any]
    ) -> IResponse[Any, Any]:
        self.logger.warning(
            'Client was rate limited (request: %s, resource: %s)',
            request.id, request.url
        )
        for _ in range(self.max_retries):
            interval = self.parse_retry_after(response)
            self.logger.debug(
                "Waiting %s seconds to retry rate limited request "
                "(request: %s, resource: %s)",
                interval, request.id, request.url
            )
            await asyncio.sleep(interval)
            response = await client.send(request)
            if response.status_code != 429:
                self.logger.critical(
                    "Rate limit lifted for client (request: %s, resource: %s)",
                    request.id, request.url
                )
                break
            self.logger.debug(
                "Rate limit not lifted for client (request: %s, resource: %s)",
                request.id, request.url
            )
        return response