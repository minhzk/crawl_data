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


class ServerDoesNotExist(Exception):
    """Raised when a server does not exist i.e. the hostname did not
    resolve when performing a DNS lookup.
    """
    __module__: str = 'headless.types'
    request: IRequest[Any]

    def __init__(
        self,
        request: IRequest[Any],
    ):
        self.request = request