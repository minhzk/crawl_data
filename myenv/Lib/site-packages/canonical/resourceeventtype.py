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
from typing import TypeVar

import pydantic


T = TypeVar('T', bound=pydantic.BaseModel)


class ResourceEventType(pydantic.BaseModel):

    @property
    def timestamp(self) -> datetime.datetime:
        return self.__root__.timestamp # type: ignore

    @classmethod
    def observe(
        cls: type[T],
        kind: str,
        params: dict[str, Any]
    ) -> T:
        return cls.parse_obj({**params, 'kind': kind})