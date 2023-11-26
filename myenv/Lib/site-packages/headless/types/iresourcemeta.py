# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

class IResourceMeta:
    content_type: str
    headers: dict[str, str]

    def get_create_url(self, **params: Any) -> str:
        raise NotImplementedError

    def get_list_url(self, **params: Any) -> str:
        raise NotImplementedError

    def get_retrieve_url(self, resource_id: int | str) -> str:
        raise NotImplementedError