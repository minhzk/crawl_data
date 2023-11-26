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
"""Declares :class:`EllipticCurveAlgorithmType`."""
import enum


class EllipticCurveAlgorithmType(str, enum.Enum):
    ES256           = 'ES256'
    ES384           = 'ES384'
    ES512           = 'ES512'
    ES256K          = 'ES256K'
    ECDH_ES         = 'ECDH-ES'
    ECDH_ES_A128KW  = 'ECDH-ES+A128KW'
    ECDH_ES_A192KW  = 'ECDH-ES+A192KW'
    ECDH_ES_A256KW  = 'ECDH-ES+A256KW'