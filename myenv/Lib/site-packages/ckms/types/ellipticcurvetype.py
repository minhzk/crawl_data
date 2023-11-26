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
"""Declares :class:`EllipticCurveType`."""
import enum


class EllipticCurveType(str, enum.Enum):
    P256    = 'P-256'
    P384    = 'P-384'
    P521    = 'P-521'
    P256K   = 'P-256K'