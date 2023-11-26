# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import AsyncIterable
from typing import Iterable
from typing import TypeAlias
from typing import Union



__all__: list[str] = [
    'RequestContent'
]

RequestContent: TypeAlias = Union[
    str,
    bytes,
    Iterable[bytes],
    AsyncIterable[bytes]
]