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
import pydantic

from ckms.ext.rfc5758.types import SignatureDigestAlgorithmType
from .algorithmidentifier import AlgorithmIdentifier
from .subjectpublickeyinfo import SubjectPublicKeyInfo


class SignatureDigestAlgorithmIdentifier(AlgorithmIdentifier):
    name: SignatureDigestAlgorithmType = pydantic.Field(..., alias='algorithm') # type: ignore

    def get_qualname(self, key: SubjectPublicKeyInfo) -> str:
        """Return the qualified name as used internally with :mod:`ckms`."""
        return self.name.qualname()