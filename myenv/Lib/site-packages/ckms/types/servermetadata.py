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
"""Declares :class:`ServerMetadata`."""
import inspect
import logging
import typing
import urllib.parse
from typing import cast
from typing import Any
from typing import Callable

import pydantic

from .ihttpclient import IHTTPClient
from .jsonwebkeyset import JSONWebKeySet
from .trustissues import AuthorizationServerMisbehaves
from .trustissues import AuthorizationServerNotDiscoverable
from .trustissues import UnresolvableIssuer


AUTH_METHODS = [
    "none",
    "client_secret_post",
    "client_secret_basic",
    "client_secret_jwt",
    "private_key_jwt",
    "tls_client_auth",
    "self_signed_tls_client_auth",
]


CONTENT_ENCRYPTION_ALGORITHMS = [
    "A128CBC-HS256",
    "A192CBC-HS384",
    "A256CBC-HS512",
    "A128GCM",
    "A192GCM",
    "A256GCM",
]

ENCRYPTION_ALGORITHMS = [
    "RSA1_5",
    "RSA-OAEP",
    "RSA-OAEP-256",
    "A128KW",
    "A192KW",
    "A256KW",
    "dir",
    "ECDH-ES",
    "ECDH-ES+A128KW",
    "ECDH-ES+A192KW",
    "ECDH-ES+A256KW",
    "A128GCMKW",
    "A192GCMKW",
    "A256GCMKW",
    "PBES2-HS256+A128KW",
    "PBES2-HS384+A192KW",
    "PBES2-HS512+A256KW",
]

SIGNATURE_ALGORITHMS = [
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "PS256",
    "PS384",
    "PS512",
    "ES256",
    "ES384",
    "ES512",
    "ES256K",
    "EdDSA"
]


class ServerMetadata(pydantic.BaseModel):
    issuer: str = pydantic.Field(
        default=None,
        title="Issuer",
        description="Authorization server's issuer identifier URL.",
        example="https://webid.unimatrixapis.com"
    )

    authorization_endpoint: str = pydantic.Field(
        default=None,
        title="Authorization endpoint",
        description="URL of the authorization server's authorization endpoint.",
        example="https://webid.unimatrixapis.com/authorize"
    )

    token_endpoint: str = pydantic.Field(
        default=None,
        title="Token endpoint",
        description="URL of the authorization server's token endpoint.",
        example="https://oauth2.unimatrixapis.com/token"
    )

    jwks_uri: typing.Optional[str] = pydantic.Field(
        default=None,
        title="JSON Web Key Set (JWKS) URI",
        description="URL of the authorization server's JWK Set document.",
        example="https://oauth2.unimatrixapis.com/jwks"
    )

    registration_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Registration endpoint",
        description=(
            "URL of the authorization server's **OAuth 2.0 Dynamic Client "
            "Registration Endpoint**."
        ),
        example="https://oauth2.unimatrixapis.com/register"
    )

    scopes_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported scopes",
        description=(
            "JSON array containing a list of the OAuth 2.0 `scope` values that "
            "this authorization server supports."
        ),
        example=["foo", "bar", "baz"]
    )

    response_types_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported response types",
        description=(
            "JSON array containing a list of the OAuth 2.0 `response_type` "
            "values that this authorization server supports."
        ),
        example=[
            "code",
            "code id_token",
            "code id_token token",
            "code token",
            "id_token",
            "id_token token",
            "none",
            "token"
        ]
    )

    response_modes_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported response modes",
        description=(
            "JSON array containing a list of the OAuth 2.0 `response_mode` "
            "values that this authorization server supports."
        ),
        example=[
            "fragment",
            "query",
        ]
    )

    grant_types_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported grant types",
        description=(
            "JSON array containing a list of the OAuth 2.0 `grant_types` "
            "values that this authorization server supports."
        ),
        example=[
            "authorization_code",
            "refresh_token",
            "client_credentials",
            "urn:ietf:params:oauth:grant-type:device_code",
            "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "urn:ietf:params:oauth:grant-type:saml2-bearer",
            "urn:ietf:params:oauth:grant-type:token-exchange",
        ]
    )

    token_endpoint_auth_methods_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported client authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this token endpoint."
        ),
        example=AUTH_METHODS
    )

    token_endpoint_auth_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the token endpoint for the signature on the JWT "
            "used to authenticate the client at the token endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    service_documentation: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Documentation",
        description=(
            "URL of a page containing human-readable information that "
            "developers might want or need to know when using the "
            "authorization server."
        ),
        example="https://oauth2.unimatrixapis.com/docs"
    )

    ui_locales_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported locals for UI",
        description=(
            "Languages and scripts supported for the user interface, "
            "represented as a JSON array of language tag values from BCP 47."
        ),
        example=["nl-NL, be"]
    )

    op_policy_uri: typing.Optional[str]= pydantic.Field(
        default=None,
        title="Data policy URL",
        description=(
            "URL that the authorization server provides to the person "
            "registering the client to read about the authorization server's "
            "requirements on how the client can use the data provided by the "
            "authorization server."
        ),
        example="https://oauth2.unimatrixapis.com/privacy"
    )

    op_tos_uri: typing.Optional[str]= pydantic.Field(
        default=None,
        title="Terms of service URL",
        description=(
            "URL that the authorization server provides to the person "
            "registering the client to read about the authorization server's "
            "terms of service."
        ),
        example="https://oauth2.unimatrixapis.com/tos"
    )

    revocation_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Revocation endpoint",
        description="URL of the authorization server's revocation endpoint.",
        example="https://oauth2.unimatrixapis.com/revoke"
    )

    revocation_endpoint_auth_methods_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this revocation endpoint."
        ),
        example=AUTH_METHODS
    )

    revocation_endpoint_auth_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the revocation endpoint for the signature on the JWT "
            "used to authenticate the client at the revocation endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    introspection_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Introspection endpoint",
        description="URL of the authorization server's introspection endpoint.",
        example="https://oauth2.unimatrixapis.com/introspect"
    )

    introspection_endpoint_auth_methods_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this introspection endpoint."
        ),
        example=AUTH_METHODS
    )

    introspection_endpoint_auth_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the introspection endpoint for the signature on the JWT "
            "used to authenticate the client at the introspection endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    signed_metadata: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Signed metadata",
        description=(
            "Signed JWT containing metadata values about the authorization "
            "server as claims."
        )
    )


    device_authorization_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Device authorization endpoint",
        description=(
            "URL of the authorization server's device authorization endpoint."
        ),
        example="https://oauth2.unimatrixapis.com/device"
    )

    tls_client_certificate_bound_access_tokens: typing.Optional[bool] = pydantic.Field(
        default=True,
        title="Supports mTLS certificate-bound access tokens",
        description=(
            "Indicates authorization server support for mutual-TLS client "
            "certificate-bound access tokens."
        ),
        example=True
    )

    mtls_endpoint_aliases: typing.Optional[typing.Dict[str, str]] = pydantic.Field(
        default={},
        title="Alternative mTLS endpoints",
        description=(
            "JSON object containing alternative authorization server "
            "endpoints, which a client intending to do mutual TLS will "
            "use in preference to the conventional endpoints."
        ),
        example={
            "authorize": "https://webid.unimatrixapis.com/authorize"
        }
    )

    nfv_token_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as NFV Token."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    nfv_token_encryption_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    nfv_token_encryption_enc_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    userinfo_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="UserInfo endpoint",
        description="URL of the authorization servers' UserInfo Endpoint.",
        example="https://webid.unimatrixapis.com/userinfo"
    )

    acr_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported ACR",
        description=(
            "JSON array containing a list of the Authentication Context Class "
            "References that this authorization server supports."
        ),
        example=["a.b", "a"]
    )

    subject_types_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported subject types",
        description=(
            "JSON array containing a list of the Subject Identifier types that "
            "this authorization server supports"
        ),
        example=["pairwise", "public"]
    )

    id_token_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as ID Token."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    id_token_encryption_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    id_token_encryption_enc_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    userinfo_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as UserInfo Endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    userinfo_encryption_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    userinfo_encryption_enc_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    request_object_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as Request Object."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    request_object_encryption_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    request_object_encryption_enc_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    display_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported display modes",
        description=(
            "JSON array containing a list of the `display` parameter values "
            "that the OpenID Provider supports."
        ),
        example=["page", "popup", "touch", "wap"]
    )

    claim_types_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claims Types "
            "that the OpenID Provider supports."
        )
    )

    claims_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claim Names of the Claims "
            "that the OpenID Provider MAY be able to supply values for."
        )
    )

    claims_locales_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported claim locales",
        description=(
            "Languages and scripts supported for values in Claims being "
            "returned, represented as a JSON array of BCP 47."
        ),
        example=["nl-NL", "be"]
    )

    claims_parameter_supported: typing.Optional[bool] = pydantic.Field(
        default=False,
        title="Supports `claims` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`claims` parameter."
        ),
        example=True
    )

    request_parameter_supported: typing.Optional[bool] = pydantic.Field(
        default=False,
        title="Supports `request` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request` parameter."
        ),
        example=True
    )

    request_uri_parameter_supported: typing.Optional[bool] = pydantic.Field(
        default=False,
        title="Supports `request_uri` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request_uri` parameter."
        ),
        example=True
    )

    require_request_uri_registration: typing.Optional[bool] = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Boolean value specifying whether the OP requires any `request_uri` "
            "values used to be pre-registered."
        ),
        example=True
    )

    require_signed_request_object: typing.Optional[bool] = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Indicates where authorization request needs to be protected as "
            "**Request Object** and provided through either `request` or "
            "`request_uri` parameter."
        ),
        example=True
    )

    pushed_authorization_request_endpoint: typing.Optional[str] = pydantic.Field(
        default=None,
        title="Pushed Authorization Request (PAR) endpoint",
        description=(
            "URL of the authorization server's pushed authorization request "
            "endpoint."
        ),
        example="https://oauth2.unimatrixapis.com/par"
    )

    require_pushed_authorization_requests: typing.Optional[bool] = pydantic.Field(
        default=False,
        title="Requires PAR?",
        description=(
            "Indicates whether the authorization server accepts authorization "
            "requests only via PAR."
        ),
        example=False
    )

    introspection_signing_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response signing."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    introspection_encryption_alg_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content key "
            "encryption (`alg` value)."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    introspection_encryption_enc_values_supported: typing.Optional[typing.List[str]] = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content "
            "encryption (`enc` value)."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    authorization_response_iss_parameter_supported: typing.Optional[bool] = pydantic.Field(
        default=True,
        title="Supports `iss` parameter in authorization response?",
        description=(
            "Boolean value indicating whether the authorization server "
            "provides the `iss` parameter in the authorization response."
        ),
        example=True
    )

    # TODO: These are non-standard properties and we must submit an RFC
    # to register these at IANA.
    token_endpoint_auth_encryption_alg_values_supported: typing.Optional[typing.List[str]] = []
    token_endpoint_auth_encryption_enc_values_supported: typing.Optional[typing.List[str]] = []
    assertion_signing_alg_values_supported: typing.Optional[typing.List[str]] = []
    assertion_encryption_alg_values_supported: typing.Optional[typing.List[str]] = []
    assertion_encryption_enc_values_supported: typing.Optional[typing.List[str]] = []
    required_encrypted_token_endpoint_auth: typing.Optional[bool] = False
    require_encrypted_assertion: typing.Optional[bool] = False

    @classmethod
    async def discover(
        cls,
        client: Any,
        issuer: str,
        path: str | None = None,
        on_failure: type[Exception] | Exception | Callable[[Exception], Exception] | None = None,
        extra_locations: list[str] | None = None,
        logger: logging.Logger | str = 'ckms.auth',
        metadata_url: str | None = None
    ) -> 'ServerMetadata':
        """Discover the metadata of an authorization server using the well-known
        endpoints.
        """
        client = cast(IHTTPClient, client)
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)
        path = f'{str.strip(path or "", "/")}/' if path is not None else ''
        extra_locations = extra_locations or []
        p = urllib.parse.urlparse(metadata_url or issuer)
        if not p.netloc or not p.scheme:
            # If there is no scheme or netloc, then the issuer is not a
            # URL, making us unable to construct the well-known metadata
            # URLs.
            raise UnresolvableIssuer
        if len(p.netloc) > 253:
            # If the domain name is longer than 253 characters, it is invalid
            # and should be considered an injection attempt.
            logger.critical("Issuer domain name exceeds maximum length")
            raise UnresolvableIssuer
        locations: list[str] = [metadata_url] if metadata_url is not None else [
            *[f'{issuer}/{str.lstrip(x, "/")}' for x in extra_locations],
            f'{issuer}/{path}.well-known/oauth-authorization-server',
            f'{issuer}/{path}.well-known/openid-configuration',
        ]
        try:
            for url in locations:
                response = client.get(
                    url=url
                )
                if inspect.isawaitable(response):
                    response = await response
                if response.status_code != 200:
                    continue
                payload = response.json()
                if inspect.isawaitable(payload):
                    payload = await payload
                break
            else:
                payload = None
        except Exception as exception:
            logger.critical(
                "Failed to retrieve authorization server metadata (%s)",
                repr(exception)
            )
            if on_failure is None:
                raise
            if callable(on_failure):
                on_failure = on_failure(exception)
            raise on_failure from exception

        if payload is None:
            raise AuthorizationServerNotDiscoverable

        try:
            return cls.parse_obj(payload)
        except pydantic.ValidationError:
            raise AuthorizationServerMisbehaves(
                hint=(
                    "The metadata returned from the well-known configuration "
                    "endpoint was of invalid format."
                )
            )

    async def get_jwks(
        self,
        client: Any
    ) -> JSONWebKeySet | None:
        """Return a :class:`~ckms.types.JSONWebKeySet` instance retrieved
        from the JWKS URI specified by the authorization server, or
        ``None``.
        """
        client = cast(IHTTPClient, client)
        if self.jwks_uri is not None:
            response = client.get(self.jwks_uri)
            if inspect.isawaitable(response):
                response = await response
            jwks = response.json()
            if inspect.isawaitable(jwks):
                jwks = await jwks
            return JSONWebKeySet.parse_obj(jwks)