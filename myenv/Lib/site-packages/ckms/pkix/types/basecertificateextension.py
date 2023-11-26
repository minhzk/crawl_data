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
from pyasn1.type import univ
from pyasn1_modules import rfc5280


class BaseCertificateExtension(pydantic.BaseModel):
    ext_id: str
    critical: bool = True

    def asn1(self) -> rfc5280.Extension:
        obj = rfc5280.Extension()
        obj['extnID'] = self.ext_id
        obj['critical'] = self.critical
        obj['extnValue'] = self.get_encoded_extension()
        return obj

    def get_encoded_extension(self) -> univ.OctetString:
        raise NotImplementedError