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
    'MaximumAgeExceeded',
    'TokenExpired',
    'TokenNotEffective',
    'WrongAudience',
]


class InvalidToken(CanonicalException):
    http_status_code: int  = 403
    code: str = "TOKEN_INVALID"
    message: str = "The supplied JSON Web Token (JWT) is not valid."
    hint: str = "Consult the documentation for the required claims and their content."


class TokenExpired(InvalidToken):
    code: str = "TOKEN_EXPIRED"
    detail: str = (
        "The 'exp' claim specified a fatal term, after which the supplied "
        "token must not be used."
    )


class TokenNotEffective(InvalidToken):
    code: str = 'TOKEN_NOT_EFFECTIVE'
    detail: str = (
        "The 'nbf' claim specified a date and time before which the token "
        "must not be accepted, and it lies in the future."
    )


class WrongAudience(InvalidToken):
    code: str = "WRONG_AUDIENCE"
    detail: str = (
        "The audience(s) specified by the 'aud' claim are not "
        "accepted by the application."
    )


class WrongIssuer(InvalidToken):
    code: str = 'WRONG_ISSUER'
    detail: str = (
        "The issuer specified by the 'iss' claim is not "
        "accepted by the application."
    )


class MaximumAgeExceeded(TokenExpired):

    def __init__(self, max_age: int, now: int, issued: int):
        super().__init__(
            detail=(
                "The JSON Web Token (JWT) exceeded the maximum age of "
                f"{max_age} seconds with {now-issued}."
            )
        )