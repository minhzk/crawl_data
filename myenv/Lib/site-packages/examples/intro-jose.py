import asyncio

import ckms
from ckms import jose


codec = jose.PayloadCodec()


async def main():
    # For this example, a key is generated. In a real-world use-case,
    # the key would be loaded from disk or reference an external key
    # management service (such as Google Cloud KMS or an HSM).
    # Be aware to NEVER use in production RSA keys with a bit length
    # lower than 2048 bits.
    await ckms.configure({
        'sig': {
            'provider': "local",
            'kty': "RSA",
            'bit_length': 2048
        },
        'enc': {
            'provider': "local",
            'kty': "RSA",
            'bit_length': 2048
        },
    })

    data = b'Hello world!'
    payload: jose.Payload = codec.encode(data)

    # Create a JWS using the `sig` key and `RS256`
    # algorithm.
    jws: jose.Payload = await payload.sign('RS256', 'sig')

    # Encrypt the JWS using the `enc` key and the default content
    # encryption algorithm (A256GCM).
    jwe: jose.Payload = await jws.encrypt('RSA-OAEP-256', 'enc')

    # Decoded the serialized JWE.
    decoded = await codec.decode(bytes(jwe))
    assert decoded == data


if __name__ == '__main__':
    asyncio.run(main())