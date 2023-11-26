# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import time
from datetime import datetime
from datetime import timezone

from canonical import AccessCode



def test_verify_valid_code():
    code = AccessCode.new()
    assert code.can_attempt()
    assert code.verify(code.secret)


def test_max_attempts_blocks_code():
    code = AccessCode.new()
    for _ in range(code.max_attempts):
        assert not code.verify('false')
    assert code.is_blocked()
    assert not code.can_attempt()


def test_expired_code():
    code = AccessCode.new()
    code.expires = datetime.now(timezone.utc)
    assert code.is_expired()
    assert not code.can_attempt()


def test_ttl_expired_code():
    code = AccessCode.new(ttl=1)
    assert not code.is_expired()
    time.sleep(1)
    assert code.is_expired()
    assert not code.can_attempt()