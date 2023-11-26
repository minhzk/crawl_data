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
# type: ignore
from typing import Any

import pydantic
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import ec
from pyasn1.type.base import Asn1Type
from pyasn1_modules import rfc2315
from pyasn1.codec.ber import decoder

from ckms.ext import asn1
from ckms.ext.pkcs.oid import SIGNED_DATA
from ckms.ext.pkcs.types import SignedData
from .timestampreq import TimeStampReq
from .tstinfo import TSTInfo


class TimeStampToken(pydantic.BaseModel):
    message: bytes
    signature: SignedData
    info: TSTInfo

    @pydantic.root_validator(pre=True)
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        if str(values.get('contentType')) != SIGNED_DATA:
            raise ValueError("Not a SignedData object")
        values['content_type'] = str(values['contentType'])
        if isinstance(values.get('content'), Asn1Type):
            obj, _ = decoder.decode(values['content'], asn1Spec=rfc2315.SignedData())
            if _:
                raise ValueError("Invalid BER-encoding")
            values['signature'] = obj
        values['message'] = bytes(asn1.decode_ber(bytes(obj['contentInfo']['content'])))
        values['info'] = TSTInfo.from_signed_data(obj['contentInfo'])
        return values

    def verify(
        self,
        certificate: x509.Certificate | None = None,
        request: TimeStampReq | None = None
    ) -> bool:
        """Verify the time stamp token using the given public key.
        
        Verify that the signer produced a signature of the correct message
        digest. The :meth:`verify()` method assumes that there is one signer.
        """
        s = self.signature.signers[0]
        if s.signed_digest != s.get_digest(bytes(self.message)):
            raise ValueError("Digest mismatch for signed data.")
        if certificate is not None:
            k: ec.EllipticCurvePublicKey | rsa.RSAPublicKey = certificate.public_key()
            s.verify(k, self.signature.content_info.content)
        if request is not None:
            if request.nonce and not self.info.nonce:
                raise ValueError("TSA did not return the nonce.")
            if request.nonce != self.info.nonce:
                raise ValueError("TSA returned a different nonce.")
        return True
