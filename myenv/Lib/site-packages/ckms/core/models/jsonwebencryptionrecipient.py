"""Declares :class:`JSONWebEncryptionRecipient`."""
import typing

import pydantic

from .octetb64 import OctetB64


class JSONWebEncryptionRecipient(pydantic.BaseModel):
    __module__: str = 'ckms.core.models'
    header: dict[str, typing.Any] = {}
    encrypted_key: OctetB64 | None = None