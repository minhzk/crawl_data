"""Supplies various helper constructs."""
import asyncio
import functools


class allow_sync:
    """Allows the synchronous execution of an async function."""

    @property
    def loop(self):
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def __init__(self, func):
        self.__func = func
        self.__loop = None
        functools.update_wrapper(self, func)

    def sync(self, *args, **kwargs):
        return self.loop.run_until_complete(self.__func(*args, **kwargs))

    async def __call__(self, *args, **kwargs):
        return await self.__func(*args, **kwargs)
