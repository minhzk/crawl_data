# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


class RateLimited(Exception):
    """Indicates that an operation was rate limited while consuming an
    external service.
    """
    __module__: str = 'canonical.exc'
    retry_after: int | None

    def __init__(
        self,
        retry_after: int | None = None
    ) -> None:
        self.retry_after = retry_after