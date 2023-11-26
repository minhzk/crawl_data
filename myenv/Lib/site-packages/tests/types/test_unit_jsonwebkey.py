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
import pytest

from ckms.types import JSONWebKey



@pytest.mark.parametrize("alg,use", [
    ("RS256", "sig"),
    ("RSA-OAEP", "enc"),
])
@pytest.mark.parametrize("path,public,asymmetric", [
    ('pki/rsa.key', False, True),
    ('pki/rsa.pub', True, True),
])
def test_frompem(path: bytes, alg: str, use: str, public: bool, asymmetric: bool):
    pem = open(path, 'rb').read()
    jwk = JSONWebKey.frompem(
        pem,
        alg=alg,
        use=use
    )
    assert jwk.is_public() is public
    assert jwk.is_asymmetric() is asymmetric
    assert jwk.alg is not None
    assert jwk.use is not None


def test_as_public_from_private():
    pem = open('pki/rsa.key', 'rb').read()
    private = JSONWebKey.frompem(
        pem,
        alg='RS256',
        use='sig'
    )
    public = private.as_public()
    p1 = public.get_public_key()
    p2 = private.get_public_key()
    assert private != public
    assert p1.public_numbers() == p2.public_numbers()


def test_as_public_from_public():
    pem = open('pki/rsa.pub', 'rb').read()
    private = JSONWebKey.frompem(
        pem,
        alg='RS256',
        use='sig'
    )
    public = private.as_public()
    assert private == public
