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
from typing import Generator


class IKeySpecification:
    __module__: str = 'ckms.types'
    algorithm: Any
    provider: Any

    def can_decrypt(self) -> bool:
        """Return a boolean indicating if the key may be used to decrypt."""
        raise NotImplementedError

    def can_encrypt(self) -> bool:
        """Return a boolean indicating if the key may be used to encrypt."""
        raise NotImplementedError

    def can_wrap(self) -> bool:
        """Return a boolean indicating if the key can wrap another key."""
        raise NotImplementedError

    def is_loaded(self) -> bool:
        """Return a boolean indicating if the specification is loaded into
        memory. Note that this regards the *metadata* and not necessarily
        the actual key material.
        """
        raise NotImplementedError

    def get_private_bytes(self) -> bytes:
        """Return the private bytes that may be used for decryption or
        signing.
        """
        raise NotImplementedError

    def get_private_key(self) -> Any:
        """Return the private key that may be used for decryption or
        signing.
        """
        raise NotImplementedError

    def get_public_key(self) -> Any:
        """Return the public key that may be used for encryption or
        verifcation.
        """
        raise NotImplementedError

    def __await__(self) -> Generator[Any, None, 'IKeySpecification']:
        return self.load().__await__()

    async def load(self) -> 'IKeySpecification':
        """Inspect the configuration and load the metadata regarding the
        key.
        """
        raise NotImplementedError