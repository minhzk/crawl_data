# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

import pydantic
from canonical import EuropeanVatNumber


VAT_NUMBERS: list[str] = [
    'PL7272445205',
    'PL5213003700',
    'PL5252242171',
    'PL7171642051',
    'DE327990207',
    'FR10402571889',
    'DK56314210',
    'ES38076731R',
    'PT501613897',
    'CZ7710043187',
    'IT06903461215',
    'BG202211464',
    'HU29312757',
    'RO14388698',
    'EL801116623',
    'FI23064613',
    'HR79147056526',
    'LT100005828314',
    'LV40203202898',
    'SK2022210311',
    'NL863726392B01',
    'BE0835221567',
    'ATU74581419',
    'CY10137629O',
    'EE100110874',
    'IE8251135U',
    'LU22108711',
    'MT26572515',
    'SE556037867001',
    'SI51510847',

    # https://www.iecomputersystems.com/ordering/eu_vat_numbers.htm
    'IE1234567X',
    'IE1X34567X',

    # https://www.avalara.com/vatlive/en/eu-vat-rules/eu-vat-number-registration/eu-vat-number-formats.html
    'FR12345678901',
    'FRX1234567890',
    'FR1X123456789',
    'FRXX123456789',

    # VIES
    'FR58832949556',
    'FR18878442284',
]


INVALID: list[str] = [
    # https://www.avalara.com/vatlive/en/eu-vat-rules/eu-vat-number-registration/eu-vat-number-formats.html
    'FRI2345678901',
    'FR1I345678901',
    'FRO2345678901',
    'FR1O345678901',
    'FROI345678901',
    'FRIO345678901',
]


class Model(pydantic.BaseModel):
    vat: EuropeanVatNumber


@pytest.mark.parametrize("vat", VAT_NUMBERS)
def test_is_valid(vat: str):
    assert EuropeanVatNumber.is_valid(vat)


@pytest.mark.parametrize("vat", INVALID)
def test_is_not_valid(vat: str):
    assert not EuropeanVatNumber.is_valid(vat)


@pytest.mark.parametrize("vat", VAT_NUMBERS)
def test_validate(vat: str):
    obj = Model.parse_obj({'vat': vat})
    assert obj.vat == vat


@pytest.mark.parametrize("vat", [
    "BE 0841.153.415"
])
def test_validate_with_invalid(vat: str):
    obj = Model(vat=vat) # type: ignore
    assert EuropeanVatNumber.is_valid(obj.vat)