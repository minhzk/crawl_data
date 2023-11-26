# type: ignore
# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .iclient import IClient
from .iclientlogger import IClientLogger
from .irequest import IRequest
from .iresponse import IResponse


class IBackoff(IClientLogger):
    __module__: str = 'headless.types'

    async def retry(
        self,
        client: 'IClient[Any, Any]',
        request: IRequest[Any],
        response: IResponse[Any, Any]
    ) -> IResponse[Any, Any]:
        raise NotImplementedError