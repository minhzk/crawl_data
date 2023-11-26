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
import inspect
import pathlib

from ckms.core.keychain import Keychain

import pytest

from ckms.pkix.types import CertificationRequest
from ckms.ext.rfc5280.types import Attribute
from ckms.ext.rfc5280.types import RelativeDistinguishedName


CURDIR: pathlib.Path = pathlib.Path(__file__).parent


@pytest.mark.parametrize("name", [
    "RS256",
    "RS384",
    "RS512",
    'ES256',
    #'ES256-384',
    #'ES256-512',
    'ES384',
    #'ES384-256',
    #'ES384-512',
    'ES512',
    #'ES512-256',
    #'ES512-512',
    'ES256K',
    #'ES256K-384',
    #'ES256K-512',
])
@pytest.mark.asyncio
async def test_sign_csr_simple(
    keychain: Keychain,
    name: str
):
    spec = keychain.get(name)
    csr = CertificationRequest.new(
        public_key=spec.get_public_key()
    )

    # Add some attributes.
    csr.add_uri('https://unimatrixone.io')
    csr.add_domain('unimatrixone.io')
    csr.add_ip('1.2.3.4')
    csr.nonrepudiable(True)
    csr.can_sign(True)
    csr.info.subject.extend([
        RelativeDistinguishedName([
            Attribute(
                type='2.5.4.6',
                value='NL'
            )
        ]),
        RelativeDistinguishedName([
            Attribute(
                type='2.5.4.7',
                value='Wezep'
            )
        ]),
        RelativeDistinguishedName([
            Attribute(
                type='2.5.4.8',
                value='Gelderland'
            )
        ]),
        RelativeDistinguishedName([
            Attribute(
                type='2.5.4.3',
                value='Cochise Ruhulessin'
            ),
            Attribute(
                type='2.5.4.42',
                value='Cochise'
            ),
            Attribute(
                type='2.5.4.43',
                value='C.Y.'
            ),
        ]),
    ])

    await csr.sign(spec)
    assert csr.signed_data
    assert csr.digest_algorithm
    is_valid = csr.verify()
    if inspect.isawaitable(is_valid):
        is_valid = await is_valid

    # Serialize and parse again to see if the signature is still
    # valid.
    der = csr.der()
    csr2 = CertificationRequest.parse_der(der)
    assert csr.info.der() == csr2.info.der()
    assert csr.signed_data == csr2.signed_data, csr2.signed_data
    is_valid = csr2.verify()
    if inspect.isawaitable(is_valid):
        is_valid = await is_valid
    assert is_valid


@pytest.mark.parametrize("fn", [
    'RS256.csr',
    'RS384.csr',
    'RS512.csr',
    'ES256.csr',
    'ES256-384.csr',
    'ES256-512.csr',
    'ES256K.csr',
    'ES256K-384.csr',
    'ES256K-512.csr',
    'ES384.csr',
    'ES384-256.csr',
    'ES384-512.csr',
    'ES512-256.csr',
    'ES512-384.csr',
    'ES512.csr',
])
@pytest.mark.asyncio
async def test_verify_from_subjectpublickeyinfo(fn: str):
    with open(CURDIR.joinpath(fn), 'rb') as f:
        csr = CertificationRequest.parse_der(f.read())
    is_valid = csr.verify()
    if inspect.isawaitable(is_valid):
        is_valid = await is_valid
    assert is_valid

    # Serialize and parse again to see if the signature is still
    # valid.
    der = csr.der()
    csr = CertificationRequest.parse_der(der)
    is_valid = csr.verify()
    if inspect.isawaitable(is_valid):
        is_valid = await is_valid
    assert is_valid
