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
import json

import pytest

from ckms.core.models import JOSEObject
from ckms.core.models.jsonwebsignature import JSONWebSignature


def test_deserialize_jws_json(multi_jws: bytes):
    obj = JOSEObject.parse(multi_jws)
    assert isinstance(obj, JSONWebSignature)