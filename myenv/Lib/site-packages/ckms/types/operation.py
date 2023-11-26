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
"""Declares :class:`Operation`."""
from typing import Any
from typing import AsyncGenerator

from .digest import Digest
from .ikeyspecification import IKeySpecification
from .message import Message
from .plaintext import PlainText


class Operation:
    """The base class for all cryptographic operations."""
    __module__: str = 'ckms.core.types'
    __abstract__: bool = True
    content: Digest | Message | PlainText
    spec: Any
    presets: dict[str, Any] = {
        'A128KW'        : {'mode': 'KEK'},
        'A192KW'        : {'mode': 'KEK'},
        'A256KW'        : {'mode': 'KEK'},
        'A128GCM'       : {'mode': 'GCM'},
        'A192GCM'       : {'mode': 'GCM'},
        'A256GCM'       : {'mode': 'GCM'},
        'A128GCMKW'     : {'mode': 'GCM'},
        'A192GCMKW'     : {'mode': 'GCM'},
        'A256GCMKW'     : {'mode': 'GCM'},
        'EdDSA'         : {},
        'ES256'         : {'digest': 'sha256'},
        'ES384'         : {'digest': 'sha384'},
        'ES512'         : {'digest': 'sha512'},
        'ES256K'        : {'digest': 'sha256'},
        'HS256'         : {},
        'HS384'         : {},
        'HS512'         : {},
        'PS256'         : {'digest': 'sha256', 'padding': 'PSS'},
        'PS384'         : {'digest': 'sha384', 'padding': 'PSS'},
        'PS512'         : {'digest': 'sha512', 'padding': 'PSS'},
        'RS256'         : {'digest': 'sha256', 'padding': 'PKCS1v15'},
        'RS384'         : {'digest': 'sha384', 'padding': 'PKCS1v15'},
        'RS512'         : {'digest': 'sha512', 'padding': 'PKCS1v15'},
        'RSA1_5'        : {'padding': 'PKCS1v15', 'digest': 'sha1'},
        'RSA-OAEP'      : {'padding': 'OAEP', 'digest': 'sha1'},
        'RSA-OAEP-256'  : {'padding': 'OAEP', 'digest': 'sha256'},
        'RSA-OAEP-384'  : {'padding': 'OAEP', 'digest': 'sha384'},
        'RSA-OAEP-512'  : {'padding': 'OAEP', 'digest': 'sha512'},
    }

    @property
    def digestmod(self) -> str | None:
        return self.content.digestmod

    @staticmethod
    def can_use_key(key: Any) -> bool:
        """Return a boolean indicating if the given `key` can be used to
        perform the operation.
        """
        return True

    @classmethod
    def fromalgorithm(
        cls,
        *,
        algorithm: str,
        **kwargs: Any
    ) -> 'Operation':
        """Create a new :class:`Operation` from a named algorithm."""
        if cls.presets:
            if algorithm not in cls.presets:
                raise NotImplementedError(f'No parameters known for {algorithm}.')
            kwargs.update(cls.presets[algorithm])
        return cls(**kwargs)

    def __init__(
        self,
        *,
        spec: Any,
        content: Digest | Message | PlainText,
        **kwargs: Any
    ):
        self.spec = spec
        if not self.can_use_key(self.spec): # pragma: no cover
            raise ValueError("Unsuitable key.")
        self.content = content

    def get_keyspec(self) -> IKeySpecification:
        return self.spec

    async def get_message(self) -> bytes:
        """Return the message on which the operation is performed."""
        message = b''
        async for chunk in self.chunks():
            message += chunk
        return message

    async def get_digest(self) -> bytes:
        """Return a digest of the message."""
        raise NotImplementedError

    def chunks(self) -> AsyncGenerator[bytes, None]:
        """Return the message to be signed."""
        return self.content.chunks()

    def get_private_key(self) -> Any:
        """Return the private key for decryption and signing."""
        return self.spec.get_private_key()

    def get_public_key(self) -> Any:
        """Return the public key for verification and encryption."""
        return self.spec.get_public_key()