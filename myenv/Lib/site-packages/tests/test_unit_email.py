# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
import pytest

from canonical import EmailAddress


@pytest.mark.parametrize('v', [
    'abc@example.com',
])
def test_validate(v: str):
    EmailAddress.validate(v)


def test_as_model_attribute():
    class Model(pydantic.BaseModel):
        email: EmailAddress

    Model.parse_obj({'email': 'abc@example.com'})


def test_domain():
    e = EmailAddress.validate('abc@example.com')
    assert e.domain == 'example.com'
