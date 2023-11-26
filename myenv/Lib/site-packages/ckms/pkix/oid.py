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


__all__: list[str] = [
    'ID_CE_BASICCONSTRAINTS',
    'ID_CE_EXTKEYUSAGE',
    'ID_CE_KEYUSAGE',
    'ID_CE_SUBJECTALTNAME',
    'ID_ECDH',
    'ID_EC_PUBLICKEY',
    'ID_EXTENSION_REQUEST',
]


ID_CE_BASICCONSTRAINTS: str = '2.5.29.19'

ID_CE_EXTKEYUSAGE: str = '2.5.29.37'

ID_CE_KEYUSAGE: str = '2.5.29.15'

ID_CE_SUBJECTALTNAME: str = '2.5.29.17'

ID_EC_PUBLICKEY: str = '1.2.840.10045.2.1'

ID_ECDH: str = '1.3.132.1.12'

ID_EXTENSION_REQUEST: str = '1.2.840.113549.1.9.14'