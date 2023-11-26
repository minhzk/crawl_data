# pylint: skip-file
import asyncio

import ckms
from ckms.jose.models import JSONWebKey
from ckms.jose import TrustedIssuers


async def main():
    external = ckms.Keychain()
    external.register({
        'sig': {
            'provider': "local",
            'kty': "OKP",
            'crv': "Ed25519",
        },
        'enc': {
            'provider': "local",
            'kty': "OKP",
            'crv': "X25519",
        },
    })
    await external.setup()

    issuers = TrustedIssuers()
    #issuers.trust("https://accounts.google.com")
    #issuers.trust("https://localhost:8000", [
    #    JSONWebKey.generate(kty='OKP', crv='Ed25519'),
    #    JSONWebKey.generate(kty='OKP', crv='Ed25519', kid='foo'),
    #])
    issuers.trust("https://localhost:8001", external)
    await issuers.setup()
    print(issuers.issuers)


if __name__ == '__main__':
    asyncio.run(main())
