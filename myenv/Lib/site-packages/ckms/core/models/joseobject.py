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
"""Declares :class:`JOSEObject`."""
import binascii
import json
from typing import Any
from typing_extensions import Annotated

import pydantic

from ckms.types import MalformedObject
from ckms.types import MalformedPayload
from ckms.utils import b64decode
from .jsonwebencryption_ import JSONWebEncryption
from .jsonwebsignature import JSONWebSignature


class JOSEObject(pydantic.BaseModel):
    __root__: Annotated[JSONWebEncryption | JSONWebSignature, pydantic.Field(discriminator='kind')]

    @classmethod
    def deserialize_compact(cls, protected: str, *segments: str) -> dict[str, Any]:
        """Deserialize a JWE or JWS that uses the compact serialization format."""
        obj: dict[str, Any]
        assert len(segments) in {2,4}
        if len(segments) == 2:
            payload, signature = segments
            obj = {
                'kind': 'JWS',
                'payload': payload,
                'signatures': [
                    {
                        'protected': protected,
                        'signature': signature
                    }
                ]
            }
        elif len(segments) == 4:
            encryption_key, iv, ciphertext, tag = segments
            obj = {
                'kind': 'JWE',
                'protected': protected,
                'recipients': [{
                    'encrypted_key': encryption_key,
                }],
                'ciphertext': ciphertext,
                'tag': tag,
                'compact': True
            }
            if iv:
                obj['iv'] = iv
        else: # pragma: no cover
            raise ValueError("Invalid number of segments in token.")
        return obj

    @classmethod
    def deserialize(cls, token: bytes | str) -> dict[str, Any]:
        """Parse a serialized JOSE object (JWE, JWS or nested JWT) from a
        byte-sequence.
        """
        if isinstance(token, bytes):
            token = bytes.decode(token, 'ascii')
        is_compact = token.find('.') != -1
        if is_compact:
            obj = {}
            if token.count('.') not in {2, 4}:
                raise MalformedObject(
                    detail="Invalid number of segments in token.",
                    hint="JOSE Compact Serialization has 3 segments for JWS, 5 for JWE."
                )
            protected, *segments = str.split(token, '.')
            obj = cls.deserialize_compact(protected, *segments)
        else:
            try:
                if not (token[0] == '{' and token[-1] == '}'):
                    # Assume here that if the token does not start and end with a bracket,
                    # we are dealing with a Base64-encoded string or byte-sequence.
                    token = bytes.decode(b64decode(token), 'utf-8')
            except (binascii.Error, IndexError, ValueError):
                raise MalformedObject

            try:
                obj: dict[str, Any] = json.loads(token)
            except ValueError:
                raise MalformedPayload

            # Determine if we are parsing a flattened JWE/JWS and convert
            # it to a general JSON object.
            if 'signature' in obj: # Flattened JWS
                obj['signatures'] = [
                    {
                        'header': obj.pop('header', {}),
                        'protected': obj.pop('protected', None),
                        'signature': obj.pop('signature', None),
                    }
                ]
                assert set(obj.keys()) >= {'payload', 'signatures'}, obj

            if 'encrypted_key' in obj: # Flattened JWE
                obj['recipients'] = [
                    {
                        'header': obj.pop('header', {}),
                        'encrypted_key': obj.pop('encrypted_key', None)
                    }
                ]

        if obj.get('recipients'):
            obj['kind'] = 'JWE'
        if obj.get('signatures'):
            obj['kind'] = 'JWS'
        obj['token'] = token
        return obj

    @classmethod
    def parse(cls, token: bytes | str) -> JSONWebEncryption | JSONWebSignature:
        obj = cls.deserialize(token=token)
        return cls.parse_obj(obj).__root__