"""Declares various helper functions related to security."""
import asyncio
import contextlib
import time
import typing


@contextlib.asynccontextmanager
async def constant(
    tmin: typing.Union[float, int]
) -> contextlib.AbstractAsyncContextManager:
    """Return a context manager that ensures that the execution time of the
    wrapped code block is constant.
    """
    t1 = time.time()
    try:
        yield
    finally:
        delta = (time.time() - t1)
        if delta < tmin:
            await asyncio.sleep(tmin - delta)
