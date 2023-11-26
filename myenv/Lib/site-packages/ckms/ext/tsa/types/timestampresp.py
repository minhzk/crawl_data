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
import pydantic

from cryptography import x509
from pyasn1_modules import rfc3161

from .pkistatusinfo import PKIStatusInfo
from .timestampreq import TimeStampReq
from .timestamptoken import TimeStampToken
from .tstinfo import TSTInfo


class TimeStampResp(pydantic.BaseModel):
    content: bytes
    request: TimeStampReq
    status: PKIStatusInfo
    token: TimeStampToken | None = pydantic.Field(
        default=None,
        alias='timeStampToken'
    )

    @classmethod
    def parse_asn1(cls, obj: rfc3161.TimeStampResp) -> 'TimeStampResp':
        return cls.parse_obj({
            'status': obj[0],
            'token': obj[1] if obj[1].isValue else None # type: ignore
        })

    @pydantic.validator('token', pre=True)
    def validate_token(
        cls,
        value: rfc3161.TimeStampToken
    ) -> rfc3161.TimeStampToken | None:
        return value if value.isValue else None

    def get_tst_info(self) -> None | TSTInfo:
        """Return a :class:`~ckms.ext.tsa.types.TSTInfo` object
        containing the timestamp metadata, if the signing was
        successful.
        """
        return self.token.info if self.token else None

    def verify(self, certificate: x509.Certificate | None = None) -> None:
        """Verify that a proper response was received from an :rfc:`3161`
        compliant Time Stamping Authority.
        """
        if not self.status.is_success():
            raise ValueError(
                "Timestamp was not granted by the Time Stamping Authority."
            )
        assert self.token is not None
        self.token.verify(
            certificate=certificate,
            request=self.request
        )