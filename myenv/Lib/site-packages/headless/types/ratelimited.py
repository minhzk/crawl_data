# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from .irequest import IRequest
from .iresponse import IResponse


class RateLimited(Exception):
    __module__: str = 'headless.types'
    request: IRequest[Any]
    response: IResponse[Any, Any]

    def __init__(
        self,
        request: IRequest[Any],
        response: IResponse[Any, Any]
    ):
        self.request = request
        self.response = response