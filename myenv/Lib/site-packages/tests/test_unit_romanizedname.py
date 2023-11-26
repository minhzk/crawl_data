# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest

from canonical import RomanizedName


@pytest.mark.parametrize("value", [
    "Renée",
    "Noël",
    "Sørina",
    "Adrián",
    "François",
    "Mary-Jo",
    "Mónica",
    "Mathéo",
    "Ruairí",
    "Mátyás",
    "Jokūbas",
    "Siân",
    "Agnès",
    "KŠthe",
])
def test_valid_names(value: str):
    assert RomanizedName.validate(value) == value


@pytest.mark.parametrize("value", [
    "1Cochise",
])
def test_invalid_names(value: str):
    with pytest.raises(ValueError):
        RomanizedName.validate(value)


@pytest.mark.parametrize("raw,cleaned", [
    (".Cochise", "Cochise"),
    (" .Cochise", "Cochise"),
    (" Cochise", "Cochise"),
    ("Cochise ", "Cochise"),
    ("Cochise.", "Cochise"),
    ("Cochise   Ruhulessin", "Cochise Ruhulessin")
])
def test_remove_unused_characters(raw: str, cleaned: str):
    assert RomanizedName.validate(raw) == cleaned


@pytest.mark.parametrize("raw,cleaned", [
    ("Mary-jane", "Mary-Jane"),
    ("Mary---jane", "Mary-Jane"),
    ('al-bezoula', 'al-Bezoula'),
    ('van der Wal', 'van der Wal'),
    ('cochise', 'Cochise'),
    ('COCHISE', 'COCHISE'),
    ('Cochise RUHULESSIN', 'Cochise RUHULESSIN')
])
def test_fix_casing(raw: str, cleaned: str):
    assert RomanizedName.validate(raw) == cleaned