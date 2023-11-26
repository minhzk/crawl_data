# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Generator


class CollectionMixin:
    """Mixin class for collection types."""
    __module__: str = 'canonical'
    openapi_title: str | None = None
    openapi_format: str | None = None
    max_length: int | None = None
    min_length: int | None = None

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title=cls.openapi_title or cls.__name__,
            type='array'
        )
        if cls.openapi_format:
            field_schema.update(format=cls.openapi_format)

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls: type[Any], v: Any) -> Any:
        return cls(v)