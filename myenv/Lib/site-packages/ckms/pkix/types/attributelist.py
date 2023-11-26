# Copyright 2022 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
from typing import Any
from typing import Sequence

from pyasn1.type import tag
from pyasn1.type import univ
from pyasn1_modules import rfc2986

from .attribute import Attribute


class AttributeList(list[Attribute]):
    _index: dict[str, int]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        value: Sequence[Attribute] | Sequence[dict[str, Any]] | univ.SetOf
    ) -> 'AttributeList':
        if isinstance(value, rfc2986.Attributes):
            value = [
                Attribute.parse_obj(x)
                for x in value # type: ignore
            ]
        for i, item in enumerate(value):
            if isinstance(item, Attribute):
                continue
            value[i] = Attribute.parse_obj(item) # type: ignore
        return cls(value or []) # type: ignore

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._index = {x.type: i for i, x in enumerate(self)}

    def add(self, obj: Attribute) -> None:
        if str(obj.type) in self._index:
            i = self._index[obj.type]
            f = functools.partial(self.__setitem__, i)
        else:
            f = self.append
            i = len(self)
            self._index[obj.type] = i
        return f(obj)

    def asn1(self) -> univ.SetOf:
        obj = rfc2986.Attributes().subtype( # type: ignore
            implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0)
        )
        obj.extend([x.asn1() for x in self]) # type: ignore
        return obj

    def get(self, oid: str) -> Attribute:
        return self[self._index[oid]] # type: ignore

    def has(self, oid: str) -> bool:
        return oid in self._index

    def pop(self, oid: str) -> Attribute: # type: ignore
        return super().pop(self._index[oid])
