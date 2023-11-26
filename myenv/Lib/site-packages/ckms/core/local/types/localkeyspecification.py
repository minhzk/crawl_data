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
from typing import Any
from typing import Literal

from ckms import types
from ckms.core import models
from ckms.core import Provider


class LocalKeySpecification(models.KeySpecification):
    kty: str | None = None # type: ignore
    provider: Literal['local'] | Provider = 'local' # type: ignore
    key: Any

    @classmethod
    def autodiscover(
        cls,
        provider: types.IProvider,
        inspector: types.IKeyInspector,
        values: dict[str, Any]
    ) -> None:
        values.update({
            'use': inspector.get_algorithm_use(values['algorithm'])
        })

    async def load(self) -> models.KeySpecification:
        """Load or generate the key as specified by the parameters."""
        assert isinstance(self.provider, types.IProvider)
        if not self.loaded:
            self.key = await self.setup_key()
        self.kid = self.provider.get_key_identifier(self)
        self.loaded = True
        return self

    async def setup_key(self):
        return await self.key.setup(self)

    def get_key_material(self) -> bytes:
        assert isinstance(self.provider, types.IProvider)
        return self.provider.inspector.to_pem(self.key)

    def has_key_material(self) -> bool:
        return True

    def get_private_key(self) -> Any:
        return self.key