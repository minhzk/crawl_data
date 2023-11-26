# Copyright 2018 Cochise Ruhulessin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unimatrix.exceptions import CanonicalException


__all__: list[str] = [
    'AuthorizationServerMisbehaves',
    'AuthorizationServerNotDiscoverable',
    'TrustIssues',
    'UnresolvableIssuer',
    'UntrustedIssuer',
    'UntrustedSigningKey',
]


class TrustIssues(CanonicalException):
    """Base class for all exceptions related to trust."""
    __module__: str = 'ckms.types'
    http_status_code: int = 403
    code: str = 'TRUST_ISSUES'
    message: str = (
        "The application was not able to establish a trust relationship "
        "with the supplied credentials, authorization server, certificate "
        "authority or other third party."
    )


class UnresolvableIssuer(TrustIssues):
    """Raised when an :term:`Issuer` is not resolvable."""
    __module__: str = 'ckms.types'
    code: str = 'UNRESOLVABLE_ISSUER'


class AuthorizationServerNotDiscoverable(TrustIssues):
    """Raised when the application fails to discover the properties of an
    authorization server through standardized discovery protocols.
    """
    __module__: str = 'ckms.types'
    code: str = 'AUTHORIZATION_SERVER_NOT_DISCOVERED'
    detail: str = (
        "The metadata of the authorization server could not be discovered "
        "using well-known URLs or other standardized protocols."
    )


class AuthorizationServerMisbehaves(TrustIssues):
    """Raises when an authorization server does not behave as expected
    based on the protocol.
    """
    __module__: str = 'ckms.types'
    http_status_code: int = 503
    code: str = 'AUTHORIZATION_SERVER_MISBEHAVES'
    detail: str = (
        "The external authorization server does not behave according to its "
        "standardized specifications."
    )


class UntrustedIssuer(TrustIssues):
    """Raised when the issuer of a credential is not trusted by the
    application.
    """
    __module__: str = 'ckms.types'
    code: str = 'UNTRUSTED_ISSUER'


class UntrustedSigningKey(TrustIssues):
    """Raised when the signing key of a credential is not trusted by the
    application.
    """
    __module__: str = 'ckms.types'
    code: str = 'UNTRUSTED_SIGNING_KEY'