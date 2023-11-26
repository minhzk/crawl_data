# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from typing import TypeVar

from .stringtype import StringType


T = TypeVar('T', bound='EuropeanVatNumber')


# https://gist.github.com/marcinlerka/630cc05d11bb10c5f1904506ff92abcd
class EuropeanVatNumber(StringType):
    patterns: re.Pattern[str] = re.compile(
        r'^('
        'ATU[0-9]{8}|'                              # Austria
        'BE0[0-9]{9}|'                              # Belgium
        'BG[0-9]{9,10}|'                            # Bulgaria
        'HR\\d{11}$|'                               # Croatia 
        'CY[0-5|9]\\d{7}[A-Z]|'                     # Cyprus
        'CZ[0-9]{8,10}|'                            # Czech Republic
        'DE[0-9]{9}|'                               # Germany
        'DK[0-9]{8}|'                               # Denmark
        'EE[0-9]{9}|'                               # Estonia
        '(EL|GR)[0-9]{9}|'                          # Greece
        'ES[0-9A-Z][0-9]{7}[0-9A-Z]|'               # Spain
        'EU\\d{9}|'                                 # EU-type 
        'FI[0-9]{8}|'                               # Finland
        'FR((?![IO])[A-Z0-9]){2}[0-9]{9}|'        # France
        'GB([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3})|' # United Kingdom
        'HU[0-9]{8}|'                               # Hungary
        'IE[0-9A-Z\\*\\+]{7}[A-Z]{1,2}|'            # Ireland
        'IT[0-9]{11}|'                              # Italy
        'LT([0-9]{9}|[0-9]{12})|'                   # Lithuania
        'LU[0-9]{8}|'                               # Luxembourg
        'LV[0-9]{11}|'                              # Latvia
        'MT[0-9]{8}|'                               # Malta
        'NL[0-9]{9}B[0-9]{2}|'                      # Netherlands
        'PL[0-9]{10}|'                              # Poland
        'PT[0-9]{9}|'                               # Portugal
        'RO[0-9]{2,10}|'                            # Romania
        'SE[0-9]{12}|'                              # Sweden
        'SI[0-9]{8}|'                               # Slovenia
        'SK[0-9]{10}|'                              # Slovakia
        'NO\\d{9}|'                                 # Norway (not EU)
        'RU\\d{10}$|\\d{12}|'                       # Russia (not EU)
        'RS\\d{9}'                                  # Serbia (not EU)
        ')$'
    )

    @staticmethod
    def clean(v: str) -> str:
        return re.sub('[^0-9A-Z]', '', str.upper(v))

    @classmethod
    def is_valid(cls, vat: str) -> bool:
        return cls.patterns.match(vat) is not None
    
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        return super().validate_pattern(cls.clean(v))