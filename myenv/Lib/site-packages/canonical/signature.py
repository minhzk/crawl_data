# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class Signature(pydantic.BaseModel):
    """A digital signature establishing the non-repudiation of a
    transaction.
    """
    alg: str = pydantic.Field(
        default=...,
        title="Algorithm",
        description=(
            "The signing algorithm used to create `signature`. Must be "
            "a valid JSON Web Algorithm (JWA)."
        )
    )

    kid: str = pydantic.Field(
        default=...,
        title="Key identifier",
        description=(
            "The key identifier of the signing key. A key identifier is "
            "generated as follows:\n\n"
            "- For keys using the **RSA** algorithm, the key identifier is "
            "the URL Safe Base64-encoded SHA-256 hash of the concatenation "
            "of the ASCII-encoded string `RSA`, `e`, and `n`. The value of "
            "`e` is encoded as a 3 octets and `n` is encoded in the number "
            "of octets of the public modulus. The expected byte order is "
            "big-endian (BE).\n\n"
            "- For keys using the **Edwards curves**, the key identifier is "
            "the URL Safe Base64-encoded SHA-256 hash of the concatenation "
            "of the ASCII-encoded string `OKP`, then the ASCII-encoded string "
            "containing the curve name (either `Ed448` or `Ed25519`, "
            "case-sensitive), and then a byte-sequence containing the public "
            "key in 'raw' encoding *and* format. The expected byte order is "
            "big-endian (BE)."
        )
    )

    digest: str = pydantic.Field(
        default=...,
        title="Digest",
        description=(
            "The URL Safe Base64-encoded SHA-384 hash of the transaction. "
            "Refer to the documentation of the specific transaction to "
            "determine how to create the digest."
        )
    )

    signature: str = pydantic.Field(
        default=...,
        title="Signature",
        description=(
            "The digital signature created with the keypair identified by "
            "`kid` from `digest`."
        )
    )