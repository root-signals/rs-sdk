import asyncio
import queue
import threading
from typing import Any, AsyncIterator, Generic, Iterator, List, Optional, TypeVar

from pydantic import StrictStr

T = TypeVar("T")


# This is internal generic class only to handle duck typing of the
# local codes' correctness.
#
# The original classes returned by partial_list may or may not have
# anything to do with this (in practise they are pydantic BaseModel
# subclasses that have no shared superclass unfortunately).
#
# Update November 2024. - This does not work well with our async iterators
# since we end up in a nested async iterator situation. Not DRY.
# Usable and left in one place with test for convenience.s
class _PartialResult(Generic[T]):
    next: Optional[StrictStr] = None
    results: Optional[List[T]] = None


async def iterate_cursor_list(partial_list: Any, *, limit: int) -> AsyncIterator[T]:
    # TODO: it would be nice to type partial_list correctly.
    cursor: Optional[StrictStr] = None
    while limit > 0:
        result: _PartialResult[T] = await partial_list(page_size=limit, cursor=cursor)
        if not result.results:
            return

        used_results = result.results[:limit]
        yield used_results  # type: ignore[misc]
        limit -= len(used_results)
        if not (cursor := result.next):
            return


# create an asyncio loop that runs in the background to
# serve our asyncio needs
loop = asyncio.get_event_loop()
if not loop.is_running():
    threading.Thread(target=loop.run_forever, daemon=True).start()


def wrap_async_iter(ait: AsyncIterator, flatten: bool = False) -> Iterator[Any]:
    """
    Wrap an asynchronous iterator into a synchronous one for our sync SDK.
    """

    q: queue.Queue = queue.Queue()
    _end = object()

    def yield_queue_items() -> Iterator[Any]:
        while True:
            next_item = q.get()
            if next_item is _end:
                break
            yield next_item
        # After observing _end we know the aiter_to_queue coroutine has
        # completed.  Invoke result() for side effect - if an exception
        # was raised by the async iterator, it will be propagated here.
        async_result.result()

    async def aiter_to_queue() -> None:
        try:
            async for item in ait:
                q.put(item)
        finally:
            q.put(_end)

    async_result = asyncio.run_coroutine_threadsafe(aiter_to_queue(), loop)
    return yield_queue_items()
