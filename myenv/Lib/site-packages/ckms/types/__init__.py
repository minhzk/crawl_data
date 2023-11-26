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
from typing import Awaitable
from typing import TypeAlias

from .aesalgorithmtype import AESAlgorithmType
from .aeskeywrapoperation import AESKeywrapOperation
from .aesoperation import AESOperation
from .algorithm import Algorithm
from .asymmetricsigningoperation import AsymmetricSigningOperation
from .audiencetype import AudienceType
from .ciphertext import CipherText
from .claimset import ClaimSet
from .cryptographicfailure import *
from .cryptographypublickeytype import CryptographyPublicKeyType
from .data import Data
from .decrypter import Decrypter
from .digest import Digest
from .edsaoperation import EdDSAOperation
from .edwardscurvealgorithmtype import EdwardsCurveAlgorithmType
from .edwardscurvetype import EdwardsCurveType
from .ellipticcurvealgorithmtype import EllipticCurveAlgorithmType
from .ellipticcurvetype import EllipticCurveType
from .ellipticcurveoperation import EllipticCurveOperation
from .encrypter import Encrypter
from .encryptoperation import EncryptOperation
from .hmacalgorithmtype import HMACAlgorithmType
from .hmacoperation import HMACOperation
from .icontentencryptionkey import IContentEncryptionKey
from .forbiddenoperation import ForbiddenOperation
from .generatekeyspec import *
from .generatekeyoperation import GenerateKeyOperation
from .ihasher import IHasher
from .ihttpclient import IHTTPClient
from .ikeychain import IKeychain
from .ikeyinspector import IKeyInspector
from .ikeyspecification import IKeySpecification
from .invalidcredential import *
from .invalidtoken import *
from .ioperationperformer import IOperationPerformer
from .iprovider import IProvider
from .jsonwebkey import JSONWebKey
from .jsonwebkeyset import JSONWebKeySet
from .jsonwebtoken import JSONWebToken
from .keyalgorithmtype import KeyAlgorithmType
from .keyoperationtype import KeyOperationType
from .keywrapoperation import KeywrapOperation
from .keyusetype import KeyUseType
from .malformed import *
from .message import Message
from .operation import Operation
from .plaintext import PlainText
from .rsaalgorithmtype import RSAAlgorithmType
from .rsaoperation import RSAOperation
from .servermetadata import ServerMetadata
from .signer import Signer
from .signingoperation import SigningOperation
from .trustissues import *
from .undecryptable import Undecryptable
from .verifier import Verifier


__all__: list[str] = [
    'Algorithm',
    'AsymmetricSigningOperation',
    'AuthorizationServerMisbehaves',
    'AuthorizationServerNotDiscoverable',
    'AESAlgorithmType',
    'AESKeywrapOperation',
    'AESOperation',
    'AudienceType',
    'CipherText',
    'ClaimSet',
    'ClaimTypeError',
    'CryptographicFailure',
    'CryptographyPublicKeyType',
    'Data',
    'Decrypter',
    'Digest',
    'EdDSAOperation',
    'EdwardsCurveAlgorithmType',
    'EdwardsCurveType',
    'EllipticCurveAlgorithmType',
    'EllipticCurveType',
    'EllipticCurveOperation',
    'Encrypter',
    'EncryptOperation',
    'HMACAlgorithmType',
    'HMACOperation',
    'ForbiddenOperation',
    'GenerateAES',
    'GenerateEllipticCurve',
    'GenerateHMAC',
    'GenerateKeyOperation',
    'GenerateKeySpec',
    'GenerateOKP',
    'GenerateRSA',
    'IContentEncryptionKey',
    'IHasher',
    'IHTTPClient',
    'IKeychain',
    'IKeyInspector',
    'IKeySpecification',
    'InvalidCredential',
    'InvalidSignature',
    'IOperationPerformer',
    'IProvider',
    'JSONWebKey',
    'JSONWebKeySet',
    'JSONWebToken',
    'KeywrapOperation',
    'KeyAlgorithmType',
    'KeyOperationType',
    'KeyType',
    'KeyUseType',
    'Malformed',
    'MalformedHeader',
    'MalformedObject',
    'MalformedPayload',
    'MaximumAgeExceeded',
    'MissingProtectedClaim',
    'MissingProtectedHeader',
    'MissingRequiredClaim',
    'Message',
    'Operation',
    'PlainText',
    'RSAAlgorithmType',
    'RSAOperation',
    'ServerMetadata',
    'Signer',
    'SigningOperation',
    'TokenExpired',
    'TokenNotEffective',
    'TrustIssues',
    'Undecryptable',
    'UnknownAlgorithm',
    'UnresolvableIssuer',
    'UntrustedIssuer',
    'UntrustedSigningKey',
    'Verifier',
    'WrongAudience',
]


EncryptResult: TypeAlias = CipherText | Awaitable[CipherText]