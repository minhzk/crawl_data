# Copyright 2018 Cochise Ruhulessin
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
from typing import cast
from typing import Any
from typing import Generator
from typing import Iterator
from typing import TypeAlias

from .decrypter import Decrypter
from .ioperationperformer import IOperationPerformer
from .verifier import Verifier


KeyType: TypeAlias = Decrypter | Verifier


class IKeychain:
    __module__: str = 'ckms.types'

    @classmethod
    def fromdict(cls, keys: dict[str, Any]) -> 'IKeychain':
        raise NotImplementedError

    def as_jwks(self, private: bool = False) -> Any:
        """Return a :class:`JSONWebKeySet` instance holding the keys
        in the instance.
        """
        raise NotImplementedError

    def dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def filter(
        self,
        algorithm: str | None = None,
        kid: str | None = None,
        use: str | None = None,
        op: str | None = None,
        keys: Any = None
    ) -> Any:
        for spec in keys:
            spec = cast(IOperationPerformer, spec)
            if not spec.is_loaded():
                raise RuntimeError("Specification is not loaded.")
            assert spec.algorithm is not None
            if algorithm is not None and spec.algorithm != algorithm:
                continue
            if use is not None and spec.use != use:
                continue
            if op is not None and not spec.can_perform(op):
                continue
        return keys

    def get(self, kid: str | None) -> KeyType:
        """Lookup a key by its key identifier."""
        raise NotImplementedError

    def tagged(self, tags: str | list[str] | set[str]) -> 'IKeychain':
        """Return a new :class:`IKeychain` instance with the keys
        matching the given tags.
        """
        raise NotImplementedError

    def has(self, kid: str | None) -> bool:
        """Return a boolean indicating if the given key identifier is in
        the keychain.
        """
        raise NotImplementedError

    def verifiers(self) -> Iterator[Verifier]:
        """Return all keys that can be used to verify a digital
        signature.
        """
        for x in self:
            if not x.can_verify():
                continue
            assert isinstance(x, Verifier)
            yield x

    def __and__(self, keychain: 'IKeychain') -> 'IKeychain':
        return self.fromdict({
            **self.dict(),
            **keychain.dict()
        })

    def __await__(self) -> Generator[Any, None, 'IKeychain']:
        raise NotImplementedError

    def __contains__(self, kid: str) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[KeyType]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError