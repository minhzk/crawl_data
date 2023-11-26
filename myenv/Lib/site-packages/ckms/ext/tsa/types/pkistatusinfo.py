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
from pyasn1_modules import rfc3161

from .pkifailureinfo import PKIFailureInfo
from .pkistatus import PKIStatus


class PKIStatusInfo(pydantic.BaseModel):
    status_code: PKIStatus = pydantic.Field(..., alias='status')
    status_message: str | None = pydantic.Field(None, alias='statusString')
    failure_reason: PKIFailureInfo | None = pydantic.Field(None, alias='failInfo')

    @pydantic.validator('status_code', pre=True)
    def validate_status_code(cls, value: int | rfc3161.PKIStatus | PKIStatus) -> int:
        if isinstance(value, rfc3161.PKIStatus):
            value = int(value)
        return value

    @pydantic.validator('status_message', pre=True)
    def validate_status_message(cls, value: str | rfc3161.PKIFreeText) -> str:
        if isinstance(value, rfc3161.PKIFreeText):
            value = str(value[0]) if value.isValue else None
        return value

    @pydantic.validator('failure_reason', pre=True)
    def validate_failure_reason(cls, value: int | rfc3161.PKIFailureInfo | PKIFailureInfo) -> str:
        if isinstance(value, rfc3161.PKIFailureInfo):
            value = int(value) if value.isValue else None
        return value

    def is_success(self) -> bool:
        """Return a boolean indicating if the status is a success."""
        return self.status_code in {PKIStatus.granted, PKIStatus.grantedWithMods}