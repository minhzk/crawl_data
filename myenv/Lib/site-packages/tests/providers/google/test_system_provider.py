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
import pytest

from ckms.core.provider.tests import AsymmetricSigningTestCase
from ckms.core.provider.tests import EncryptionTestCase
from ckms.core.provider.tests import ProviderTestCase
from ckms.core.provider.tests import SymmetricSigningTestCase

from .conftest import ENCRYPTION_KEYS
from .conftest import SIGNING_KEYS_ASYMMETRIC
from .conftest import SIGNING_KEYS_SYMMETRIC


class TestGoogleProviderFacilities(ProviderTestCase):
    name: str = 'google'


@pytest.mark.parametrize("spec", SIGNING_KEYS_ASYMMETRIC)
class TestGoogleAsymmetricSign(AsymmetricSigningTestCase):
    name: str = 'google'


@pytest.mark.parametrize("spec", SIGNING_KEYS_SYMMETRIC)
class TestGoogleSymmetricSign(SymmetricSigningTestCase):
    name: str = 'google'


@pytest.mark.parametrize("spec", ENCRYPTION_KEYS)
class TestGoogleEncryption(EncryptionTestCase):
    name: str = 'google'