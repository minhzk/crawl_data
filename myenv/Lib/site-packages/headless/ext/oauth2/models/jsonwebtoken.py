# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from types import NotImplementedType
from typing import TypeVar

import pydantic
from ckms.jose import Decoder
from ckms.types import Malformed


T = TypeVar('T', bound='JSONWebToken')


class JSONWebToken(pydantic.BaseModel):
    _token: str = pydantic.PrivateAttr(None)

    @classmethod
    def parse_jwt(
        cls: type[T],
        token: str,
        accept: set[str] | NotImplementedType = NotImplemented,
        **extra: Any
    ) -> T:
        typ = None
        try:
            jose, jwt = Decoder.introspect(token)
        except Malformed:
            raise ValueError('malformed JSON Web Token')
        for header in jose.headers:
            if header.typ is None:
                continue
            typ = str.lower(header.typ)
            break
        else:
            typ = None
        if jwt is None:
            raise ValueError('could not decode JSON Web Token.')
        if accept != NotImplemented and typ not in accept:
            raise TypeError(f'Invalid JWT type: {str(typ)[:16]}')
        self = cls.parse_obj({**jwt.dict(), **extra})
        self._token = token
        return self