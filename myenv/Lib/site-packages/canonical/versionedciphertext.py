# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from typing import Any

import ckms.utils
import pydantic
from ckms.core import KeySpecification
from ckms.types import CipherText


DEFAULT_CHUNK_SIZE: int = 255


class VersionedCipherText(pydantic.BaseModel):
    aad: str | None = None
    ct: str | list[str]
    dsn: str
    enc: str | None = None
    iv: str | None = None
    tag: str | None = None

    @pydantic.root_validator(pre=True) # type: ignore
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        ct: bytes | str | list[str] | None = values.get('ct')
        if isinstance(ct, (bytes, str)):
            # Split the cipher text up in chunks because some storage
            # backends have limits on the size of a value. This excludes
            # systems that do no support an array data type, but otherwise
            # we cannot predict if the storage system is able to store the
            # value.
            if isinstance(ct, bytes):
                ct = ckms.utils.b64encode_str(ct)
            values.update({
                'ct': [
                    ct[i:i+DEFAULT_CHUNK_SIZE]
                    for i in range(0, len(ct), DEFAULT_CHUNK_SIZE)
                ]
            })
            assert str.join('', values['ct']) == ct
        return values

    @pydantic.validator('iv', 'aad', 'tag', pre=True) # type: ignore
    def preprocess_bytes(cls, value: bytes | str | None) -> str | None:
        if isinstance(value, bytes):
            value = ckms.utils.b64encode_str(value)
        return value

    def get_ciphertext(self) -> bytes:
        ct = self.ct
        if not isinstance(ct, str):
            ct = str.join('', ct)
        return ckms.utils.b64decode(ct)

    async def decrypt(self, key: KeySpecification) -> bytes:
        params: dict[str, bytes] = {}
        if self.aad: params['aad'] = ckms.utils.b64decode(self.aad)
        if self.iv: params['iv'] = ckms.utils.b64decode(self.iv)
        if self.tag: params['tag'] = ckms.utils.b64decode(self.tag)
        ct = CipherText(buf=self.get_ciphertext(), **params)
        result = key.decrypt(ct)
        if inspect.isawaitable(result):
            result = await result
        assert isinstance(result, bytes)
        return result