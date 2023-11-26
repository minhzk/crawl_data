# Copyright 2018 Cochise Ruhulessin
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
"""Declares :class:`Recipient`."""
import pydantic

from .octetb64 import OctetB64
from .joseheader_ import JOSEHeader


class Recipient(pydantic.BaseModel):
    header: JOSEHeader
    encrypted_key: OctetB64

    @property
    def alg(self) -> str | None:
        return self.header.alg

    @property
    def kid(self) -> str | None:
        return self.header.kid

    @property
    def iv(self) -> bytes | None:
        return self.header.iv

    @property
    def tag(self) -> bytes | None:
        return self.header.tag