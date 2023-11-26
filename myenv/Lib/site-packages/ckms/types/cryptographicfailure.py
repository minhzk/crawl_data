# pylint: skip-file
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
from unimatrix.exceptions import CanonicalException


__all__: list[str] = [
    'CryptographicFailure',
    'UnknownAlgorithm',
]


class CryptographicFailure(CanonicalException):
    __module__: str = 'ckms.types'
    http_status_code: int = 500
    code: str = 'CRYPTOGRAPHIC_FAILURE'
    message: str = (
        "An error occurred while performing a cryptographic operation. "
        "That's all we know."
    )


class UnknownAlgorithm(CryptographicFailure):
    __module__: str = 'ckms.types'
    algorithm: str
    http_status_code: int = 403
    code: str = "UNKNOWN_CRYPTOGRAPHIC_ALGORITHM"
    message: str = (
        "The cryptographic algorithm is not supported by the application. "
        "Consult the documentation for the list of supported algorithms."
    )

    def __init__(self, name: str):
        self.algorithm = name
        super().__init__()

    def __repr__(self) -> str:
        return f'<{type(self).__name__}: {self.algorithm} (id: {self.id})>'