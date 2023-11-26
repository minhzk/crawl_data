# Copyright (C) 2020-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`GrantType`."""
import enum


__all__: list[str] = [
    'GrantType',
]


class GrantType(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    authorization_code = "authorization_code"
    client_credentials = "client_credentials"
    refresh_token = "refresh_token"
    jwt_bearer = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    saml_bearer = "urn:ietf:params:oauth:grant-type:saml2-bearer"
    session = "urn:webid:params:oauth:grant-type:session"

    #: See https://www.rfc-editor.org/rfc/rfc8628
    device_code = "urn:ietf:params:oauth:grant-type:device_code"