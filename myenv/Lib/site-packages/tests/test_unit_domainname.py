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

from canonical import DomainName


@pytest.mark.parametrize('v', [
    'com',
    'example.com',
    'www.example.com',
    '_.example.com',
    'localhost'
])
def test_validate(v: str):
    DomainName.validate(v)


@pytest.mark.parametrize('v', [
    'abc@example.com',
    '-foo',
    'foo-',
    '-foo.bar',
    'foo.bar-',
    f'{"a" * 64}',
    f'{"a" * 64}.com',
])
def test_invalid(v: str):
    with pytest.raises(ValueError):
        DomainName.validate(v)


@pytest.mark.parametrize('v', [
    'com',
    'example.com',
    'www.example.com',
    'localhost'
])
def test_as_model_attribute(v: str):
    class Model(pydantic.BaseModel):
        domain: DomainName

    Model.parse_obj({'domain': v})