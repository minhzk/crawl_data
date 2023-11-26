"""Declares :class:`TrustedIssuers`."""
import asyncio
import warnings
from typing import Any
from typing import Generator

import httpx # TODO

from ckms.core import Keychain
from ckms.types import TrustIssues
from ckms.types import JSONWebKey
from ckms.types import JSONWebKeySet
from ckms.types import ServerMetadata


class TrustedIssuers:
    """Maintains a registry of trusted issuers and their signing/encryption
    keys.
    """
    deferred: object = object()
    issuers: dict[str, JSONWebKeySet]
    trusted: set[str]
    UntrustedIssuer: type[Exception] = type('UntrustedIssuer', (Exception,), {})

    @staticmethod
    def default() -> 'TrustedIssuers':
        """Return a :class:`TrustedIssuers` instance that is integrated
        with the settings module.
        """
        return _default

    @staticmethod
    def normalize_issuer(issuer: str) -> str:
        if not str.startswith(issuer, "https://"):
            issuer = f'https://{issuer}'
        return issuer

    def __init__(
        self,
        trusted: set[str] | None = None
    ):
        self.issuers = {}
        self.trusted = trusted or set()

    def get(self, issuer: str) -> JSONWebKeySet:
        """Return a :class:`JSONWebKeySet` holding the keys of the
        given `issuer`, or raise :exc:`ckms.types.TrustIssues`.
        """
        if issuer not in self.issuers:
            raise TrustIssues(
                detail=(
                    "The issuer of the credential attached to the request "
                    "is not trusted by the application."
                )
            )
        return self.issuers[issuer]

    def is_trusted(self, issuer: str | None) -> bool:
        """Return a boolean indicating if the given issuer is trusted."""
        return issuer in self.issuers

    def trust(
        self,
        issuer: str,
        keys: list[JSONWebKey] | JSONWebKeySet | Keychain | None = None
    ) -> None:
        """Add a trusted issuer to the registry.

        If the `keys` parameter is provided, no attempt is made to fetch
        the issuers' keys using any mechanism.
        """
        issuer = self.normalize_issuer(issuer)
        self.trusted.add(issuer)
        if keys is not None:
            if isinstance(keys, Keychain):
                keys = keys.as_jwks(private=False)
            elif isinstance(keys, list):
                keys = JSONWebKeySet(keys=keys)
            self.issuers[issuer] = keys

    async def setup(self) -> 'TrustedIssuers':
        """Fetch the remote keys for all issuers and setup the
        :class:`~ckms.types.JSONWebKeySet` instances.
        """
        async with httpx.AsyncClient(verify=False) as client:
            await asyncio.gather(*[
                self.setup_issuer(client, x)
                for x in self.trusted
            ])
        return self

    async def setup_issuer(
        self,
        client: httpx.AsyncClient,
        issuer: str,
        retry: int = 5,
        _attempts: int = 0
    ) -> None:
        """Setup the previously registered issuer `issuer`."""
        # Figure out the issuer URL. If it is a domain, prepend https. We assume
        # the OAuth 2.0 discovery protocol here.
        if str.startswith(issuer, 'http://'):
            raise ValueError("Can not fetch issuer keys over HTTP.")
        try:
            metadata = await ServerMetadata.discover(issuer=issuer, client=client)
            jwks = await metadata.get_jwks(client=client)
        except Exception:
            if _attempts >= retry:
                raise
            warnings.warn(f"Unable to reach issuer {issuer}")
            await asyncio.sleep(1)
            return await self.setup_issuer(
                client=client,
                issuer=issuer,
                retry=retry,
                _attempts=_attempts + 1
            )

        if jwks is None:
            raise ValueError(f"Unable to retrieve issuer JWKS: {issuer}")
        assert jwks is not None
        self.issuers[issuer] = jwks

    def verify_jws(self, jws: bytes | str) -> bool:
        """Verifies a JSON Web Signature (JWS) issued by one of the
        trusted issuers.
        """
        return False

    def __await__(self) -> Generator[Any, None, 'TrustedIssuers']:
        return self.setup().__await__()


_default: TrustedIssuers = TrustedIssuers()
