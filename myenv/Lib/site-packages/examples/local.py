import asyncio

import ckms.core


async def main():
    # Generate an RSA key, marked for use with the 'PS256' algorithm, using
    # the 'local' cryptographic operations provider - an implementation
    # that performs the operations using in-memory key material.
    spec = ckms.core.parse_spec({
        'provider': 'local',
        'kty': 'RSA',
        'algorithm': 'PS256',
        'key': {'length': 2048}
    })

    # Before using a key, it must be configured once by awaiting it.
    # Alternatively, the ckms.core.parse_spec() call may be awaited.
    await spec

    data = b'Hello world!'
    sig = await spec.sign(data)
    assert await spec.verify(sig, data)
    assert not await spec.verify(sig, b'Not the signed data')


if __name__ == '__main__':
    asyncio.run(main())
