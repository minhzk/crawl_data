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

from canonical import ResourceName


class Model(pydantic.BaseModel):
    resource: ResourceName


def test_init_valid_resource_id():
    rn = ResourceName('//mock.unimatrixapis.com/books/1')
    assert str(rn.service) == 'mock.unimatrixapis.com'
    assert rn.relname == 'books/1'


@pytest.mark.parametrize("v", [
    "//mock.unimatrixapis.com/",
    "//mock.unimatrixapis.com",
])
def test_relname_is_required(v: str):
    with pytest.raises(ValueError):
        ResourceName(v)


@pytest.mark.parametrize("v", [
    "/mock.unimatrixapis.com/books/1",
    "mock.unimatrixapis.com/books/1",
])
def test_preceding_slashes_required(v: str):
    with pytest.raises(ValueError):
        ResourceName(v)


def test_model_valid_resource_id():
    obj = Model.parse_obj({'resource': '//mock.unimatrixapis.com/books/1'})
    assert isinstance(obj.resource, ResourceName)


@pytest.mark.parametrize("v", [
    "/mock.unimatrixapis.com/books/1",
    "mock.unimatrixapis.com/books/1",
    "//mock.unimatrixapis.com/",
    "//mock.unimatrixapis.com",
])
def test_model_invalid(v: str):
    with pytest.raises(ValueError):
        Model.parse_obj({'resource': v})