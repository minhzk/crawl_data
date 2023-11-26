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
from ckms.types import MalformedObject
from ckms.utils import b64decode


def test_deserialize_jwe_json(multi_jwe: bytes):
    obj = JOSEObject.deserialize(multi_jwe)
    assert len(obj['recipients']) == 2
    assert obj['recipients'][0]['header']['foo'] == 1
    assert 'protected' in obj
    assert 'iv' in obj
    assert 'tag' in obj
    assert 'ciphertext' in obj
    assert 'aad' not in obj
    assert 'header' not in obj
    assert 'unprotected' not in obj
    assert 'encrypted_key' not in obj


def test_deserialize_jwe_flattened(flattened_jwe: bytes):
    obj = JOSEObject.deserialize(flattened_jwe)
    protected = json.loads(b64decode(obj['protected']))
    header = obj['recipients'][0]['header']
    assert 'protected' in obj
    assert 'iv' in obj
    assert 'tag' in obj
    assert 'ciphertext' in obj
    assert 'aad' not in obj
    assert 'header' not in obj
    assert 'unprotected' not in obj
    assert 'encrypted_key' not in obj
    assert protected['foo'] == 1
    assert header['bar'] == 1


def test_deserialize_jwe_compact(compact_jwe: bytes):
    obj = JOSEObject.deserialize(compact_jwe)
    protected = json.loads(b64decode(obj['protected']))
    assert 'protected' in obj
    assert 'iv' in obj
    assert 'tag' in obj
    assert 'aad' not in obj
    assert 'ciphertext' in obj
    assert 'header' not in obj
    assert 'unprotected' not in obj
    assert 'encrypted_key' not in obj
    assert 'foo' in protected


def test_deserialize_jws_json(multi_jws: bytes):
    obj = JOSEObject.deserialize(multi_jws)
    assert len(obj['signatures']) == 2
    assert 'protected' in obj['signatures'][0]
    assert 'protected' in obj['signatures'][1]


def test_deserialize_jws_flattened(flattened_jws: bytes):
    obj = JOSEObject.deserialize(flattened_jws)
    header = json.loads(b64decode(obj['signatures'][0]['protected']))
    assert 'payload' in obj
    assert 'signatures' in obj
    assert 'header' not in obj
    assert 'protected' not in obj
    assert header.get('foo') == 1
    assert obj['signatures'][0]['header'].get('bar') == 1


def test_deserialize_jws_compact(compact_jws: bytes):
    obj = JOSEObject.deserialize(compact_jws)
    assert 'payload' in obj
    assert 'signatures' in obj
    assert len(obj['signatures']) == 1


@pytest.mark.parametrize("token", [
    'e', # No segments
    'e.e', # Not enough segments
    'e.e.e.', # Too many segments for signature
    'e.e.e.e.e.e', # Too many segments for encryption,
    'foo', # Invalid base64 encoding
])
def test_malformed_token_raises_malformed_token(token: str):
    with pytest.raises(MalformedObject):
        JOSEObject.deserialize(token)