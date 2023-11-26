# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical import dto

from .v1 import Account as AccountV1


__all__: list[str] = [
    'Account',
    'AccountV1'
]


class Account(dto.VersionedDTO):
    __root__: AccountV1

    @property
    def spec(self):
        return self.__root__.spec