# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ServerMetadata`."""
from typing import Any

import pydantic

from .clientauthenticationmethod import ClientAuthenticationMethod


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
    issuer: str | None = pydantic.Field(
        default=None,
        title="Issuer",
        description="Authorization server's issuer identifier URL.",
        example="https://webid.unimatrixapis.com"
    )

    authorization_endpoint: str | None = pydantic.Field(
        default=None,
        title="Authorization endpoint",
        description="URL of the authorization server's authorization endpoint.",
        example="https://webid.unimatrixapis.com/authorize"
    )

    token_endpoint: str | None = pydantic.Field(
        default=None,
        title="Token endpoint",
        description="URL of the authorization server's token endpoint.",
        example="https://oauth2.unimatrixapis.com/token"
    )

    jwks_uri: str | None = pydantic.Field(
        default=None,
        title="JSON Web Key Set (JWKS) URI",
        description="URL of the authorization server's JWK Set document.",
        example="https://oauth2.unimatrixapis.com/jwks"
    )

    registration_endpoint: str | None = pydantic.Field(
        default=None,
        title="Registration endpoint",
        description=(
            "URL of the authorization server's **OAuth 2.0 Dynamic Client "
            "Registration Endpoint**."
        ),
        example="https://oauth2.unimatrixapis.com/register"
    )

    scopes_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported scopes",
        description=(
            "JSON array containing a list of the OAuth 2.0 `scope` values that "
            "this authorization server supports."
        ),
        example=["foo", "bar", "baz"]
    )

    response_types_supported: list[str] | None = pydantic.Field(
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

    response_modes_supported: list[str] | None = pydantic.Field(
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

    grant_types_supported: list[str] | None = pydantic.Field(
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

    token_endpoint_auth_methods_supported: list[ClientAuthenticationMethod] = pydantic.Field(
        default=[],
        title="Supported client authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this token endpoint."
        ),
        example=AUTH_METHODS
    )

    token_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the token endpoint for the signature on the JWT "
            "used to authenticate the client at the token endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    service_documentation: str | None = pydantic.Field(
        default=None,
        title="Documentation",
        description=(
            "URL of a page containing human-readable information that "
            "developers might want or need to know when using the "
            "authorization server."
        ),
        example="https://oauth2.unimatrixapis.com/docs"
    )

    ui_locales_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported locals for UI",
        description=(
            "Languages and scripts supported for the user interface, "
            "represented as a JSON array of language tag values from BCP 47."
        ),
        example=["nl-NL, be"]
    )

    op_policy_uri: str | None= pydantic.Field(
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

    op_tos_uri: str | None= pydantic.Field(
        default=None,
        title="Terms of service URL",
        description=(
            "URL that the authorization server provides to the person "
            "registering the client to read about the authorization server's "
            "terms of service."
        ),
        example="https://oauth2.unimatrixapis.com/tos"
    )

    revocation_endpoint: str | None = pydantic.Field(
        default=None,
        title="Revocation endpoint",
        description="URL of the authorization server's revocation endpoint.",
        example="https://oauth2.unimatrixapis.com/revoke"
    )

    revocation_endpoint_auth_methods_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this revocation endpoint."
        ),
        example=AUTH_METHODS
    )

    revocation_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the revocation endpoint for the signature on the JWT "
            "used to authenticate the client at the revocation endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    introspection_endpoint: str | None = pydantic.Field(
        default=None,
        title="Introspection endpoint",
        description="URL of the authorization server's introspection endpoint.",
        example="https://oauth2.unimatrixapis.com/introspect"
    )

    introspection_endpoint_auth_methods_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this introspection endpoint."
        ),
        example=AUTH_METHODS
    )

    introspection_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the introspection endpoint for the signature on the JWT "
            "used to authenticate the client at the introspection endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    signed_metadata: str | None = pydantic.Field(
        default=None,
        title="Signed metadata",
        description=(
            "Signed JWT containing metadata values about the authorization "
            "server as claims."
        )
    )


    device_authorization_endpoint: str | None = pydantic.Field(
        default=None,
        title="Device authorization endpoint",
        description=(
            "URL of the authorization server's device authorization endpoint."
        ),
        example="https://oauth2.unimatrixapis.com/device"
    )

    tls_client_certificate_bound_access_tokens: bool | None = pydantic.Field(
        default=True,
        title="Supports mTLS certificate-bound access tokens",
        description=(
            "Indicates authorization server support for mutual-TLS client "
            "certificate-bound access tokens."
        ),
        example=True
    )

    mtls_endpoint_aliases: dict[str, str] | None = pydantic.Field(
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

    nfv_token_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as NFV Token."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    nfv_token_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    nfv_token_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    userinfo_endpoint: str | None = pydantic.Field(
        default=None,
        title="UserInfo endpoint",
        description="URL of the authorization servers' UserInfo Endpoint.",
        example="https://webid.unimatrixapis.com/userinfo"
    )

    acr_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported ACR",
        description=(
            "JSON array containing a list of the Authentication Context Class "
            "References that this authorization server supports."
        ),
        example=["a.b", "a"]
    )

    subject_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported subject types",
        description=(
            "JSON array containing a list of the Subject Identifier types that "
            "this authorization server supports"
        ),
        example=["pairwise", "public"]
    )

    id_token_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as ID Token."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    id_token_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    id_token_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    userinfo_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as UserInfo Endpoint."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    userinfo_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    userinfo_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    request_object_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as Request Object."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    request_object_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    request_object_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    display_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported display modes",
        description=(
            "JSON array containing a list of the `display` parameter values "
            "that the OpenID Provider supports."
        ),
        example=["page", "popup", "touch", "wap"]
    )

    claim_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claims Types "
            "that the OpenID Provider supports."
        )
    )

    claims_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claim Names of the Claims "
            "that the OpenID Provider MAY be able to supply values for."
        )
    )

    claims_locales_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported claim locales",
        description=(
            "Languages and scripts supported for values in Claims being "
            "returned, represented as a JSON array of BCP 47."
        ),
        example=["nl-NL", "be"]
    )

    claims_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `claims` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`claims` parameter."
        ),
        example=True
    )

    request_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `request` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request` parameter."
        ),
        example=True
    )

    request_uri_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `request_uri` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request_uri` parameter."
        ),
        example=True
    )

    require_request_uri_registration: bool | None = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Boolean value specifying whether the OP requires any `request_uri` "
            "values used to be pre-registered."
        ),
        example=True
    )

    require_signed_request_object: bool | None = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Indicates where authorization request needs to be protected as "
            "**Request Object** and provided through either `request` or "
            "`request_uri` parameter."
        ),
        example=True
    )

    pushed_authorization_request_endpoint: str | None = pydantic.Field(
        default=None,
        title="Pushed Authorization Request (PAR) endpoint",
        description=(
            "URL of the authorization server's pushed authorization request "
            "endpoint."
        ),
        example="https://oauth2.unimatrixapis.com/par"
    )

    require_pushed_authorization_requests: bool | None = pydantic.Field(
        default=False,
        title="Requires PAR?",
        description=(
            "Indicates whether the authorization server accepts authorization "
            "requests only via PAR."
        ),
        example=False
    )

    introspection_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response signing."
        ),
        example=SIGNATURE_ALGORITHMS
    )

    introspection_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content key "
            "encryption (`alg` value)."
        ),
        example=ENCRYPTION_ALGORITHMS
    )

    introspection_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content "
            "encryption (`enc` value)."
        ),
        example=CONTENT_ENCRYPTION_ALGORITHMS
    )

    authorization_response_iss_parameter_supported: bool | None = pydantic.Field(
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
    #token_endpoint_auth_encryption_alg_values_supported: list[str] | None = []
    #token_endpoint_auth_encryption_enc_values_supported: list[str] | None = []
    #assertion_signing_alg_values_supported: list[str] | None = []
    #assertion_encryption_alg_values_supported: list[str] | None = []
    #assertion_encryption_enc_values_supported: list[str] | None = []
    #required_encrypted_token_endpoint_auth: bool | None = False
    #require_encrypted_assertion: bool | None = False

    @pydantic.root_validator(pre=True)
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        values.setdefault('token_endpoint_auth_methods_supported', [])
        return values

    @pydantic.validator('token_endpoint_auth_methods_supported')
    def preprocess_token_endpoint_auth_methods_supported(
        cls,
        value: list[Any] | None 
    ) -> list[Any]:
        if value is None:
            value = []
        return value

    def supports_response_mode(self, response_mode: Any) -> bool:
        """Return a boolean indicating if the server supports the
        given response mode.
        """
        return bool(self.response_modes_supported)\
            and response_mode in self.response_modes_supported