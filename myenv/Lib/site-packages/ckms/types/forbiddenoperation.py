# Copyright 2022 Cochise Ruhulessin
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
from unimatrix.exceptions import CanonicalException

from .keyoperationtype import KeyOperationType


class ForbiddenOperation(CanonicalException):
    __module__: str = 'ckms.types'
    http_status_code: int = 403
    code: str = 'CRYPTOGRAPHIC_OPERATION_FORBIDDEN'
    message: str = "Unable to perform the requested cryptographic operation."

    def __init__(self, op: KeyOperationType):
        super().__init__( # type: ignore
            detail=(
                "The request was rejected because the cryptographic key "
                f"is not allowed to perform the '{op.value}' operation."
            )
        )
        self.op = op