"""Declares :class:`JSONWebEncryption`."""
import typing

import pydantic

from .jsonwebencryptionrecipient import JSONWebEncryptionRecipient
from .jsonwebencryptionflattened import JSONWebEncryptionFlattened
from .jsonwebencryptionwithrecipients import JSONWebEncryptionWithRecipients
from .jsonb64 import JSONB64


class JSONWebEncryption(pydantic.BaseModel):
    __module__: str = 'ckms.core.models'
    __root__: typing.Union[
        JSONWebEncryptionFlattened,
        JSONWebEncryptionWithRecipients
    ]

    @property
    def header(self) -> dict[str, typing.Any]:
        """The JOSE header containing the metadata describing the
        encryption and the encrypted object.
        """
        return self.__root__.get_header()

    @property
    def recipients(self) -> list[JSONWebEncryptionRecipient]:
        return self.__root__.recipients

    @classmethod
    def parse_compact(cls, token: bytes) -> 'JSONWebEncryption':
        protected, encryption_key, iv, ciphertext, tag = token.split(b'.')
        return cls.parse_obj({
            'protected': protected,
            'unprotected': {},
            'header': {},
            'encrypted_key': encryption_key,
            'iv': iv,
            'ciphertext': ciphertext,
            'tag': tag,
            'aad': None
        })

    @pydantic.root_validator(allow_reuse=True)
    def validate_protected(cls, values: dict[str, typing.Any]):
        dto = typing.cast(
            typing.Union[
                JSONWebEncryptionFlattened,
                JSONWebEncryptionWithRecipients
            ],
            values.get('__root__')
        )
        protected = typing.cast(JSONB64, dto.protected or {})
        unprotected = dto.unprotected

        # The Header Parameter values used when creating or validating
        # per-recipient ciphertext and Authentication Tag values are
        # the union of the three sets of Header Parameter values that
        # may be present: (1) the JWE Protected Header represented in
        # the "protected" member, (2) the JWE Shared Unprotected Header
        # represented in the "unprotected" member, and (3) the JWE
        # Per-Recipient Unprotected Header represented in the "header"
        # member of the recipient's array element.  The union of these
        # sets of Header Parameters comprises the JOSE Header.  The
        # Header Parameter names in the three locations MUST be
        # disjoint (RFC 7516, Section 7.2.1).
        if set(protected.keys()) & set(unprotected.keys()):
            raise ValueError(
                "Parameters in protected and unprotected headers "
                "must be disjoint."
            )

        headers = {**protected, **unprotected}
        if isinstance(dto, JSONWebEncryptionFlattened):
            if bool(set(headers.keys()) & set(dto.header.keys())):
                raise ValueError(
                    "Parameters in protected, unprotected and recipient "
                    "headers must be disjoint."
                )

        for i, recipient in enumerate((dto.recipients)):
            if isinstance(dto, JSONWebEncryptionFlattened)\
            or not bool(set(recipient.header.keys()) & set(headers.keys())):
                continue
            raise ValueError(
                "Parameters in protected, unprotected and recipient "
                f"headers must be disjoint. Recipient {i} specified "
                "a header that was already in the protected or "
                "unprotected headers."
            )

        return values