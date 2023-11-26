import asyncio

import ckms.core


async def main():
    keys = [
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'aes256gcm',
            'version': 3
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'ec_sign_secp256k1_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'ec_sign_p256_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'ec_sign_p384_sha384',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_2048_sha1',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_2048_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_3072_sha1',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_3072_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_4096_sha1',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_4096_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_decrypt_oaep_4096_sha512',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pss_2048_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pss_3072_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pss_4096_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pss_4096_sha512',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pkcs1_2048_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pkcs1_3072_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pkcs1_4096_sha256',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'rsa_sign_pkcs1_4096_sha512',
            'version': 1
        }),
        ckms.core.parse_spec({
            'provider': 'google',
            'project': 'unimatrixdev',
            'location': 'europe-west4',
            'keyring': 'local',
            'key': 'hmac_sha256',
            'version': 1
        })
    ]
    await asyncio.gather(*keys)
    for k in keys:
        print(f'Key {k.kid}, {k.kty}, {k.algorithm}')


if __name__ == '__main__':
    asyncio.run(main())

