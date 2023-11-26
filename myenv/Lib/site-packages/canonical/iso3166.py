# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Generator

import iso3166
from pydantic.validators import str_validator


# Corrections for wrong names
COUNTRY_NAMES: dict[str, str] = {
    'NL': 'The Netherlands'
}

# Additional codes that are not in the iso3166 library (TODO: make issue at Github)
_records: list[iso3166.Country] = [
    # This one is problematic because it only has an ISO 3166 Alpha 2 code.
    iso3166.Country("Northern Ireland", "XI", 'GBR', '826', "Northern Ireland"),
]

# Another EU peculiarity: The European Commission generally uses
# ISO 3166-1 alpha-2 codes with two exceptions: EL (not GR) is
# used to represent Greece, and UK (not GB) is used to represent
# the United Kingdom.[10][11] This notwithstanding, the Official
# Journal of the European Communities specified that GR and GB be
# used to represent Greece and United Kingdom respectively.[12]
# For VAT administration purposes, the European Commission uses
# EL and GB for Greece and the United Kingdom respectively.
# https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
_eu_alpha2_mapping: dict[str, iso3166.Country] = {
    'EL': iso3166.countries_by_alpha2['GR'],
    'UK': iso3166.countries_by_alpha2['GB']
}

_alpha2_eu_mapping: dict[str, str] = {v.alpha2: k for k, v in _eu_alpha2_mapping.items()}

countries_by_alpha2: dict[str, iso3166.Country] = {
    x.alpha2: x
    for x in _records
}


class ISO3166Base(str):
    length: int

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., str | None], None, None]:
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if len(v) != cls.length:
            raise ValueError('Value is not an ISO 3166 code.')
        try:
            return cls(cls._get_country(v))
        except LookupError:
            raise ValueError(f"Invalid code: {v}")

    @classmethod
    def _get_country(cls, v: str) -> str:
        raise NotImplementedError


class ISO3166Alpha2(ISO3166Base):
    length: int = 2

    @property
    def name(self) -> str:
        if str(self) in COUNTRY_NAMES:
            return COUNTRY_NAMES[self]
        c = iso3166.countries_by_alpha2.get(self)
        if c is None:
            raise LookupError
        return c.name

    @classmethod
    def __modify_schema__(
        cls,
        field_schema: dict[str, Any]
    ) -> None:
        field_schema.update( # pragma: no cover
            title='Country code',
            description='An ISO 3166 alpha-2 country code.',
            type='string',
        )

    @classmethod
    def _get_country(cls, v: str) -> str:
        c = countries_by_alpha2.get(v)\
            or iso3166.countries_by_alpha2.get(v)\
            or _eu_alpha2_mapping.get(v)
        if c is None:
            raise LookupError
        return c.alpha2