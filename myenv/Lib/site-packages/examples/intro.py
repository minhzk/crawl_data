import asyncio

import ckms


async def main():
    await ckms.configure({
        'example': {
            'provider': "local",
            'path': "pki/rsa.key"
        }
    })

    msg = b"Hello world!"
    sig = await ckms.sign(msg, using='example', algorithm='RS256')
    assert await ckms.verify(
        signature=sig,
        data=msg,
        using='example',
        algorithm='RS256'
    )

    assert not await ckms.verify(
        signature=sig,
        data=b'foo',
        using='example',
        algorithm='RS256'
    )


if __name__ == '__main__':
    asyncio.run(main())
