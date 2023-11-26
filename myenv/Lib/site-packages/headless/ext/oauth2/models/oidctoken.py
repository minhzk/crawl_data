# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical import EmailAddress

from .jsonwebtoken import JSONWebToken
from .subjectidentifier import SubjectIdentifier


class OIDCToken(JSONWebToken):
    iss: str
    sub: str
    exp: int
    aud: str| list[str]
    iat: int
    auth_time: int | None = None
    nonce: str | None = None
    acr: str = "0"
    amr: list[str] = []
    azp: str | None = None

    # Standard claims
    email: EmailAddress | None = None
    email_verified: bool = False
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    middle_name: str | None = None
    nickname: str | None = None
    preferred_username: str | None = None
    profile: str | None = None
    picture: str | None = None

    @property
    def principals(self) -> list[EmailAddress | SubjectIdentifier]:
        values = [
            self.email,
            SubjectIdentifier(iss=self.iss, sub=self.sub)
        ]
        return [x for x in values if x is not None]