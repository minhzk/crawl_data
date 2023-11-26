"""Declares :class:`JSONWebEncryptionFlattened`."""
import typing

from .jsonwebencryptionbase import JSONWebEncryptionBase
from .jsonwebencryptionrecipient import JSONWebEncryptionRecipient
from .octetb64 import OctetB64


class JSONWebEncryptionFlattened(JSONWebEncryptionBase):
    header: dict[str, typing.Any] = {}
    encrypted_key: OctetB64

    @property
    def recipients(self) -> list[JSONWebEncryptionRecipient]:
        return [
            JSONWebEncryptionRecipient(
                header=self.header,
                encrypted_key=OctetB64(self.encrypted_key)
            )
        ]

    def get_header(self) -> dict[str, typing.Any]:
        return {**super().get_header(), **self.header}