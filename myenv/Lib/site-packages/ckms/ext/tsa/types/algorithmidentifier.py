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
# type: ignore
from pyasn1.type.univ import ObjectIdentifier
from pyasn1_modules import rfc2459


HASHING_ALGORITHM_OIDS: dict[str, ObjectIdentifier] = {
    'sha1'  : ObjectIdentifier((1,3,14,3,2,26)),
    'sha256': ObjectIdentifier((2,16,840,1,101,3,4,2,1,)),
    'sha384': ObjectIdentifier((2,16,840,1,101,3,4,2,2,)),
    'sha512': ObjectIdentifier((2,16,840,1,101,3,4,2,3,))
}


class AlgorithmIdentifier(rfc2459.AlgorithmIdentifier):

    @classmethod
    def new(cls, name: str) -> 'AlgorithmIdentifier':
        """Create a new :class:`AlgorithmIdentifier` by name."""
        instance = cls()
        instance.setComponentByPosition(0, HASHING_ALGORITHM_OIDS[name])
        return instance