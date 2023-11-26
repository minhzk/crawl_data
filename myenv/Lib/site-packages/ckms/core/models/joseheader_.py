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
"""Declares :class:`JOSEHeader`."""
from ckms.types import ClaimSet

from .octetb64 import OctetB64


class JOSEHeader(ClaimSet):
    """Contains the claims specified in a JOSE header."""
    __module__: str = 'ckms.types'
    alg: str | None
    cty: str | None
    enc: str | None
    kid: str | None
    iv: OctetB64 | None
    tag: OctetB64 | None
    typ: str | None
    jku: str | None