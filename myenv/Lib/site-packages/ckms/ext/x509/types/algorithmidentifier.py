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
import enum
import hashlib

from cryptography.hazmat.primitives import hashes


class AlgorithmIdentifier(str, enum.Enum):
    sha1    = '1.3.14.3.2.26'
    sha256  = '2.16.840.1.101.3.4.2.1'
    sha384  = '2.16.840.1.101.3.4.2.2'
    sha512  = '2.16.840.1.101.3.4.2.3'
    sha224  = '2.16.840.1.101.3.4.2.4'

    @property
    def hasher_class(self) -> type[hashes.Hash]:
        return getattr(hashes, str.upper(self.name))

    def digest(self, data: bytes) -> bytes:
        return getattr(hashlib, self.name)(data).digest()