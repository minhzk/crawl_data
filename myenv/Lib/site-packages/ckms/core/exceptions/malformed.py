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
from unimatrix.exceptions import CanonicalException


__all__: list[str] = [
    'Malformed',
    'MissingProtectedClaim',
    'MissingProtectedHeader'
]


class Malformed(CanonicalException):
    __module__: str = 'ckms.core.types'
    http_status_code: int = 403


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