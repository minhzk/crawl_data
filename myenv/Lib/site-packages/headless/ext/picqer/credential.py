# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from headless.types import BasicAuth
from headless.types import IRequest


class PicqerCredential(BasicAuth):
    api_email: str

    def __init__(self, api_email: str, api_key: str):
        super().__init__(username=api_key, password='x')
        self.api_email = api_email

    async def add_to_request(self, request: IRequest[Any]) -> None:
        await super().add_to_request(request)
        request.add_header(
            'User-Agent',
            f'Headless (picqer.com/api - {self.api_email})'
        )