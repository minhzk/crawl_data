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
from typing import Callable
from typing import Generator

from ..cryptographicfailure import UnknownAlgorithm


class Algorithm(str):
    """The base class for all cryptographic algorithms."""
    __module__: str = 'ckms.algorithm'
    _aliases: dict[str, str] = {}
    _defaults: dict[tuple[str, str], 'Algorithm'] = {}
    _registry: dict[str, 'Algorithm'] = {}
    allowed_ops: list[str]
    default_ops: list[str]
    digest: str | None
    digest_oid: str | None
    padding: str | None
    kty: str
    use: str

    @classmethod
    def alias(cls, name: str, alias_of: str) -> None:
        cls._aliases[name] = alias_of

    @classmethod
    def default(cls, kty: str, use: str) -> 'Algorithm':
        return Algorithm._defaults[(kty, use)]

    @classmethod
    def get(cls, name: str) -> 'Algorithm':
        if name in cls._aliases:
            name = cls._aliases[name]
        return cls._registry[name]

    @classmethod
    def get_for_curve(cls, curve: str) -> 'Algorithm':
        # TODO:
        curves = {
            'P-256': 'ES256',
            'P-384': 'ES384',
            'P-521': 'ES512',
            'P-256K': 'ES256K',
        }
        return cls.get(curves[curve])

    @staticmethod
    def register(
        name: str,
        *,
        base: type['Algorithm'],
        **params: Any
    ) -> None:
        """Register a new algorithm preset using the given class."""
        Algorithm._registry[name] = base(name, **params)

    @classmethod
    def __get_validators__(
        cls
    ) -> Generator[Callable[..., 'Algorithm'], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> 'Algorithm':
        if str(value) not in Algorithm._registry:
            raise UnknownAlgorithm(value)
        if isinstance(value, cls): # pragma: no cover
            return value
        return Algorithm._registry[value]

    def __new__(
        cls,
        name: str,
        allowed_ops: set[str] | None = None,
        default_ops: set[str] | None = None,
        digest: str | None = None,
        digest_oid: str | None = None,
        padding: str | None = None,
        kty: str | None = None,
        use: str | None = None,
        crv: str | None = None,
        default: bool = False,
        *args: Any,
        **kwargs: Any
    ):
        if name in Algorithm._aliases:
            name = Algorithm._aliases[name]
        if name in Algorithm._registry:
            return Algorithm._registry[name]

        self = str.__new__(cls, name)
        self.allowed_ops = allowed_ops or set()
        self.default_ops = default_ops or set()
        self.digest = digest
        self.digest_oid = digest_oid
        self.padding = padding
        self.use = use # type: ignore
        if kty is not None:
            self.kty = kty
        if kty and use and default:
            Algorithm._defaults[(kty, use)] = self
        return self

    def get_digest_oid(self) -> str | None:
        """Return the Object Identifier (OID) for this algorithm when
        used to create a digital signature.
        """
        return self.digest_oid

    def get_key_ops(self, public: bool) -> list[str]:
        """Return the default allowed key operations for this algorithm."""
        if not public:
            return self.default_ops
        ops: list[str] = []
        if 'decrypt' in self.default_ops:
            ops.append('encrypt')
        if 'sign' in self.default_ops:
            ops.append('verify')
        if 'unwrapKey' in self.default_ops:
            ops.append('wrapKey')
        return ops


    def get_hasher(self) -> Any:
        """Return the hasher used to perform a cryptographic operation."""
        raise NotImplementedError

    def get_padding(self) -> Any:
        """Return an instance of the padding, if the algorithm implements it."""
        raise NotImplementedError