# pylint: skip-file
import pytest

from .conftest import SIGNING_ALGORITHMS


@pytest.mark.parametrize("using,algorithm", SIGNING_ALGORITHMS)
class TestSigning:

	@pytest.mark.asyncio
	async def test_sign(self, keychain, data, using, algorithm):
		sig = await keychain.sign(data=data, using=using, algorithm=algorithm)
		assert await keychain.verify(signature=sig, data=data, using=using, algorithm=algorithm)
