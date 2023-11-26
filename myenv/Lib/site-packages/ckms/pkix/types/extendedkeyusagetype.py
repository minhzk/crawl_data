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
from ckms.ext.asn1 import ObjectIdentifierEnum


class ExtendedKeyUsageType(str, ObjectIdentifierEnum):
    serverAuth          = '1.3.6.1.5.5.7.3.1'
    clientAuth          = '1.3.6.1.5.5.7.3.2'
    codeSigning         = '1.3.6.1.5.5.7.3.3'
    emailProtection     = '1.3.6.1.5.5.7.3.4'
    ipSecEndSystem      = '1.3.6.1.5.5.7.3.5'
    ipSecTunnel         = '1.3.6.1.5.5.7.3.6'
    ipSecUser           = '1.3.6.1.5.5.7.3.7'
    timeStamping        = '1.3.6.1.5.5.7.3.8'
    ocspSigning         = '1.3.6.1.5.5.7.3.9'
    secureShellClient   = '1.3.6.1.5.5.7.3.21'
    secureShellServer   = '1.3.6.1.5.5.7.3.22'