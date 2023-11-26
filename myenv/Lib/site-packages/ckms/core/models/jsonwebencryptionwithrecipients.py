"""Declares :class:`JSONWebEncryptionWithRecipients`."""
import typing

from .jsonwebencryptionbase import JSONWebEncryptionBase
from .jsonwebencryptionrecipient import JSONWebEncryptionRecipient


class JSONWebEncryptionWithRecipients(JSONWebEncryptionBase):
    __module__: str = 'ckms.core.models'
    recipients: list[JSONWebEncryptionRecipient]

    def get_header(self) -> dict[str, typing.Any]:
        return {**self.protected, **self.unprotected}