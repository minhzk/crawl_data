# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ..resource import TeamleaderResource


class User(TeamleaderResource):
    id: str
    first_name: str
    last_name: str
    email: str
    #TODO: telephones
    language: str
    function: str | None = None
    timezone: str = 'Europe/Amsterdam'
    status: str = 'active'

    class Meta(TeamleaderResource.Meta):
        base_endpoint: str = '/users'