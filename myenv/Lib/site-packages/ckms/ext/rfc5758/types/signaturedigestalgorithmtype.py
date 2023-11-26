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
from ckms.ext import asn1


class SignatureDigestAlgorithmType(str, asn1.ObjectIdentifierEnum):
    # RFC 4055
    RSA_SHA256 = '1.2.840.113549.1.1.11'
    RSA_SHA384 = '1.2.840.113549.1.1.12'
    RSA_SHA512 = '1.2.840.113549.1.1.13'
    RSA_SHA224 = '1.2.840.113549.1.1.14'

    # RFC 5758
    ECDSA_SHA224 = '1.2.840.10045.4.3.1'
    ECDSA_SHA256 = '1.2.840.10045.4.3.2'
    ECDSA_SHA384 = '1.2.840.10045.4.3.3'
    ECDSA_SHA512 = '1.2.840.10045.4.3.4'

    def qualname(self) -> str:
        """Returns the default JWA-like algorithm."""
        alg = self.name[-3:]
        if str.startswith(self.name, 'RSA'):
            alg = f'RS{alg}'
        if str.startswith(self.name, 'ECDSA'):
            alg = f'ES{alg}'
        return alg