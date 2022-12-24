import asyncio
import typing as t
import functools

import dramatiq


T = t.TypeVar("T")
P = t.ParamSpec("P")


def run_sync(fn: t.Callable[P, t.Coroutine[t.Any, t.Any, T]]) -> t.Callable[P, T]:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper


@dramatiq.actor
@run_sync
async def hello_world(name: str) -> None:
    print(f"hello {name}")
