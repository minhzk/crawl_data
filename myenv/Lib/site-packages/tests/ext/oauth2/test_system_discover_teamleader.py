# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pytest

from headless.ext.oauth2.test.manual import *
from headless.ext.oauth2.models import ClientAuthenticationMethod


@pytest.fixture
def server_url() -> str:
    return ''


@pytest.fixture
def server_params() -> dict[str, Any]:
    return {
        'client_id': '95426b7f8f3878a21468201b165a2371',
        'client_auth': ClientAuthenticationMethod.client_secret_post,
        'client_secret': 'af5fd177321185f9ba36c78fb0a72cd5',
        'authorization_endpoint': 'https://focus.teamleader.eu/oauth2/authorize',
        'token_endpoint': 'https://focus.teamleader.eu/oauth2/access_token',
        'token_endpoint_auth_methods_supported': [
            ClientAuthenticationMethod.client_secret_post
        ]
    }