"""Declares :class:`JSONWebEncryptionBase`."""
import typing

import pydantic

from .jsonb64 import JSONB64
from .octetb64 import OctetB64


class JSONWebEncryptionBase(pydantic.BaseModel):
    __module__: str = 'ckms.core.models'
    protected: JSONB64 = JSONB64()
    unprotected: dict[str, typing.Any] = {}
    iv: OctetB64 | None = None
    aad: OctetB64 | None = None
    ciphertext: OctetB64
    tag: OctetB64 | None

    def get_header(self) -> dict[str, typing.Any]:
        return {
            **self.unprotected,
            **typing.cast(dict[str, typing.Any], self.protected or {}),
        }