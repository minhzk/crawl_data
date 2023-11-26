# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Any

from canonical import EmailAddress

from headless.types import IResponse
from .picqerresource import PicqerResource


class User(PicqerResource):
    iduser: int
    username: str
    firstname: str
    lastname: str
    emailaddress: EmailAddress

    # Mismatch with docs: language can be null
    language: str | None
    admin: bool
    active: bool
    last_login_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None = None

    @classmethod
    def get_next_url(
        cls,
        response: IResponse[Any, Any],
        n: int
    ) -> str | None:
        if n == 0:
            raise StopIteration
        offset = int(dict(response.request.params).get('offset') or 0)
        return cls._meta.get_list_url(offset=offset + 100)

    class Meta:
        base_endpoint: str = '/v1/users'