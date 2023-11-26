# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

from ..resource import TeamleaderResource
from .user import User


T = TypeVar('T', bound='CurrentUser')


class CurrentUser(User):
    #TODO: preferences
    whitelabeling: bool = False

    @classmethod
    def get_retrieve_url(cls: type[T], resource_id: int | str | None) -> str:
        return f'{cls._meta.base_endpoint}.me'

    class Meta(TeamleaderResource.Meta): # type: ignore
        base_endpoint: str = '/users'