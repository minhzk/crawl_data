import asyncio

from ckms.jose.models import JSONWebKeySet


async def main():
    jwks = await JSONWebKeySet.discover("https://accounts.google.com")
    print(jwks)


if __name__ == '__main__':
    asyncio.run(main())