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
"""Declares :class:`IProvider`."""
import importlib
from typing import cast
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generator
from typing import TypeAlias
from typing import Union

from unimatrix.exceptions import CanonicalException

from ckms.lib import dsnparse
from .generatekeyoperation import GenerateKeyOperation
from .ikeyinspector import IKeyInspector
from .undecryptable import Undecryptable # type: ignore


class IProvider:
    __module__: str = 'cbra.types'
    SignResult: TypeAlias = bytes | Awaitable[bytes]
    Undecryptable: type[CanonicalException] = Undecryptable
    _default_providers: dict[str, str] = {
        'azure': 'ckms.ext.azure.AzureProvider',
        'google': 'ckms.ext.google.GoogleProvider',
        'local': 'ckms.core.local.LocalProvider',
        'random': 'ckms.core.random.RandomProvider',
        'ssh-agent': 'ckms.ext.ssh.provider.SSHAgentProvider',
    }
    _providers: dict[str, 'IProvider'] = {}
    inspector: IKeyInspector

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., 'IProvider'], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, 'IProvider']):
        if isinstance(value, str):
            value = cls.get(value)
        return value

    @staticmethod
    def get(name: str) -> 'IProvider':
        """Return the provider implementation specified by the `name`
        argument.
        """
        if name not in IProvider._providers:
            ProviderImpl = cast(type[IProvider], IProvider.load_impl(name))
            IProvider._providers[name] = ProviderImpl()
        return IProvider._providers[name]

    @staticmethod
    def load_impl(name: str) -> type['IProvider']:
        """Loads the implementation class `name`."""
        module_name, symbol = str.rsplit(IProvider._default_providers[name], '.', 1)
        return getattr(importlib.import_module(module_name), symbol)

    @staticmethod
    def register(name: str, qualname: str) -> None:
        """Registers a new provider implementation under the given name."""
        IProvider._default_providers[name] = qualname # pragma: no cover

    def calculate_kid(self, value: Any) -> Any:
        return self.inspector.calculate_kid(value)

    def jwk(self, spec: Any, private: bool, **claims: Any) -> Any:
        """Create a JWK from a key specification."""
        raise NotImplementedError

    def parse_dsn(self, dsn: dsnparse.ParseResult) -> Any:
        """Parse a key specification from a Data Source Name (DSN)."""
        raise NotImplementedError

    def decrypt(
        self,
        key: Any,
        algorithm: str,
        ciphertext: Any
    ) -> Any | Awaitable[Any]:
        """Decrypt a cipher test using the given algorithm."""
        raise NotImplementedError

    def encrypt(
        self,
        key: Any,
        algorithm: str,
        plaintext: Any,
        **kwargs: Any
    ) -> Any | Awaitable[Any]:
        """Encrypt message using the given algorithm."""
        raise NotImplementedError

    def wrap(
        self,
        key: Any,
        algorithm: str,
        wrap: Any,
        **kwargs: Any
    ) -> Any | Awaitable[Any]:
        """Wrap a key using the given algorithm."""
        raise NotImplementedError

    async def fetch(self, blob: Any) -> bytes:
        """Fetches the content of the remote blob using the parameters
        specified. Return a byte-string holding the content.
        """
        raise NotImplementedError

    async def generate(self, op: GenerateKeyOperation) -> Any:
        """Generate a new private key."""
        raise NotImplementedError

    async def load(self, key: Any) -> None:
        """Loads the key metadata and updates its properties."""
        raise NotImplementedError

    async def random(self, length: int) -> bytes:
        """Return a random byte-sequence of the given length."""
        raise NotImplementedError

    def get_hashing_algorithm(self, algorithm: str) -> str | None:
        """Return a string indicating the hashing algorithm."""
        raise NotImplementedError

    def get_key_identifier(self, spec: Any) -> str: # type: ignore
        """Generate a key identifier for the given private key."""
        raise NotImplementedError

    def get_public_key(self, spec: Any) -> Any | None:
        """Return a :class:`~ckms.core.types.PublicKeySpecification`
        instance representing the public part of an asymmetric keypair,
        or ``None`` if `spec` is not an asymmetric key.
        """
        raise NotImplementedError

    def parse_spec(self, spec: dict[str, Any]) -> Any:
        """Parse a key specification from a dictionary."""
        raise NotImplementedError

    def sign(
        self,
        key: Any,
        algorithm: str,
        message: Any
    ) -> bytes | Awaitable[bytes]:
        """Sign message using the given algorithm."""
        raise NotImplementedError

    def validate_provider(self) -> Any: # type: ignore
        """Validate the parameters as required by the provider and return
        the updated instance.
        """
        raise NotImplementedError

    def verify(
        self,
        key: Any,
        algorithm: str,
        message: Any,
        signature: bytes
    ) -> bool | Awaitable[bool]:
        """Verify a digital signature, specified by the operation."""
        raise NotImplementedError