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
"""Declares :class:`RSAAlgorithmType`."""
import enum


class RSAAlgorithmType(str, enum.Enum):
    RS256       = 'RS256'
    RS384       = 'RS384'
    RS512       = 'RS512'
    PS256       = 'PS256'
    PS384       = 'PS384'
    PS512       = 'PS512'
    RSA1_5      = 'RSA1_5'
    RSA_OAEP    = 'RSA-OAEP'
    RSA_OAEP256 = 'RSA-OAEP-256'
    RSA_OAEP384 = 'RSA-OAEP-384'
    RSA_OAEP512 = 'RSA-OAEP-512'