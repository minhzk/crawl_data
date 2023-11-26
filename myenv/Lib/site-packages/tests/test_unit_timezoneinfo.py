# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest
import pytz

from canonical import TimezoneInfo



@pytest.mark.parametrize("timezone",
    [x for x in pytz.all_timezones if '/' in x] # type: ignore
)
def test_verify_valid_zone(timezone: str):
    TimezoneInfo.validate(timezone)


def test_unknown_zone_raises_valueerror():
    with pytest.raises(ValueError):
        TimezoneInfo.validate('foo')