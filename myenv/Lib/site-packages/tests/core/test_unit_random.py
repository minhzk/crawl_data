# pylint: skip-file
import pytest

from ckms import core


@pytest.mark.asyncio
async def test_random_length():
    provider = core.provider('random')
    assert len(await provider.random(16)) == 16