# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic


def NameField(*args: Any, **kwargs: Any) -> Any:
    kwargs.setdefault('min_length', 2)
    kwargs.setdefault('max_length', 30)
    kwargs.setdefault('regex', "^([ \u00c0-\u01ffa-zA-Z'\\-])+$")
    return pydantic.Field(*args, **kwargs)