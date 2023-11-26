# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TypeVar

import pydantic


T = TypeVar('T', bound='AccessCode')


class AccessCode(pydantic.BaseModel):
    attempts: int = 0
    expires: datetime | None = None
    generation: int = 1
    max_attempts: int = 10
    max_generations: int
    length: int
    secret: str

    @staticmethod
    def generate(length: int) -> str:
        return str(secrets.randbelow((10**length) - 1)).zfill(length)

    @classmethod
    def new(
        cls: type[T],
        length: int = 6,
        max_attempts: int = 10,
        max_generations: int = 1,
        ttl: int | None = None
    ) -> T:
        expires = None
        if ttl is not None:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(seconds=ttl)
        return cls(
            expires=expires,
            length=length,
            max_attempts=max_attempts,
            secret=cls.generate(length),
            max_generations=max_generations
        )
    
    def can_attempt(self) -> bool:
        """Return a boolean indicating if this code may be attempted
        to verify.
        """
        return all([
            not self.is_blocked(),
            not self.is_expired()
        ])

    def can_rotate(self) -> bool:
        """Return a boolean indicating if the access token may rotate."""
        return self.generation < self.max_generations

    def is_blocked(self) -> bool:
        """Return a boolean indicating if the access code is a blocked
        based on the number of attempts and maximum attempts.
        """
        return self.attempts >= self.max_attempts

    def is_expired(self) -> bool:
        """Return a boolean indicating if the :class:`AccessCode` is
        expired.
        """
        return datetime.now(timezone.utc) >= self.expires if self.expires else False

    def rotate(self) -> None:
        """Rotate the access code."""
        self.attempts = 0
        self.generation += 1
        self.secret = self.generate(self.length)

    def verify(self, value: str) -> bool:
        """Verify that value matches the access code."""
        value = str.replace(value, '-', '')
        is_valid = secrets.compare_digest(self.secret, value)
        if not is_valid:
            self.attempts += 1
        if self.is_blocked() and self.can_rotate():
            self.rotate()
        return is_valid