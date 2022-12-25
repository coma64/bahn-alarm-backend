import typing as t
import functools
import asyncio

INSIDE_DRAMATIQ = False

T = t.TypeVar("T")
X = t.TypeVar("X")
Y = t.TypeVar("Y")
P = t.ParamSpec("P")

# If we're not inside a running event loop we're inside a dramatiq worker (no async support) and
# therefore need to create the event loop ourselves
try:
    event_loop = asyncio.get_running_loop()
except RuntimeError:
    INSIDE_DRAMATIQ = True
    event_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(event_loop)


def run_async(
    fn: t.Callable[P, t.Coroutine[X, Y, T]]
) -> t.Callable[P, T] | t.Callable[P, t.Coroutine[X, Y, T]]:
    """Augments a function such that it stays a coroutine if it's running inside an event loop
    but becomes a normal function if it's not.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # get_running_loop() throws if we're not already inside a coroutine
            asyncio.get_running_loop()
            return fn(*args, **kwargs)
        except RuntimeError:
            return event_loop.run_until_complete(fn(*args, **kwargs))

    return wrapper
