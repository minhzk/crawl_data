# Copyright 2022 Cochise Ruhulessin
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
from typing import Any

from unimatrix.exceptions import CanonicalException


__all__: list[str] = [
    'ClaimTypeError',
    'Malformed',
    'MalformedHeader',
    'MalformedObject',
    'MalformedPayload',
    'MissingProtectedClaim',
    'MissingProtectedHeader',
    'MissingRequiredClaim',
]


class Malformed(CanonicalException):
    __module__: str = 'ckms.core.types'
    http_status_code: int = 400


class MalformedObject(Malformed):
    code: str = 'MALFORMED_JOSE_OBJECT'
    message: str = (
        "The application refuses to complete the request because the JOSE "
        "object was malformed and could not be parsed."
    )


class MalformedHeader(Malformed):
    code: str = 'MALFORMED_JOSE_HEADER'
    message: str = (
        "The application refuses to complete the request because the JOSE "
        "header of the attached object was malformed."
    )


class MalformedPayload(Malformed):
    code: str = "MALFORMED_JOSE_PAYLOAD"
    message: str = (
        "The payload of the JOSE object included in the request is "
        "malformed and could not be interpreted by the application."
    )


class ClaimTypeError(Malformed):
    code: str = 'CLAIM_TYPE_ERROR'
    message: str = (
        "The data type of claim violated the specification."
    )

    def __init__(self, claim: str, **kwargs: Any):
        super().__init__(
            detail=(
                f"The '{claim}' claim contains an invalid data type."
            ),
            **kwargs
        )


class MissingProtectedHeader(Malformed):
    http_status_code: int = 403
    code: str = 'MISSING_PROTECTED_HEADER'
    message: str = (
        "The JSON Web Signature (JWS) did not include a protected header "
        "for one or more signatures."
    )


class MissingProtectedClaim(Malformed):
    claim: str

    def __init__(self, name: str):
        self.claim = name
        super().__init__( # type: ignore
            message="A required claim was missing from the protected JOSE header.",
            detail=(
                f"The '{name}' claim was not included in the JOSE header and "
                "the application requires it to succcesfully validate the token."
            )
        )


class MissingRequiredClaim(Malformed):
    code: str = "CLAIM_REQUIRED"
    claim: str

    def __init__(self, name: str):
        self.claim = name
        super().__init__( # type: ignore
            message="A required claim was missing from the JSON Web Token (JWT).",
            detail=(
                f"The '{name}' claim was not included in the JWT and "
                "the application requires it to succcesfully validate the token."
            )
        )

