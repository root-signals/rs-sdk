from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    ContextManager,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
)

from pydantic import StrictStr
from typing_extensions import TypeAlias

from .generated import openapi_aclient, openapi_client

T = TypeVar("T")


ClientContextCallable: TypeAlias = Union[
    Callable[[], ContextManager[openapi_client.ApiClient]], Callable[[], AsyncContextManager[openapi_aclient.ApiClient]]
]


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


async def aiterate_cursor_list(partial_list: Any, *, limit: int) -> AsyncIterator[T]:
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


def iterate_cursor_list(partial_list: Any, *, limit: int) -> Iterator[T]:
    # TODO: it would be nice to type partial_list correctly.
    cursor: Optional[StrictStr] = None
    while limit > 0:
        result: _PartialResult[T] = partial_list(page_size=limit, cursor=cursor)
        if not result.results:
            return
        used_results = result.results[:limit]
        yield from used_results
        limit -= len(used_results)
        if not (cursor := result.next):
            return


def with_sync_client(func: Callable) -> Callable:
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        context = self.client_context()
        assert isinstance(context, AbstractContextManager), "This method is not available in asynchronous mode"
        with context as client:
            return func(self, *args, _client=client, **kwargs)

    return wrapper


def with_async_client(func: Callable) -> Callable:
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        context = self.client_context()
        assert isinstance(context, AbstractAsyncContextManager), "This method is not available in synchronous mode"
        async with context as client:
            return await func(self, *args, _client=client, **kwargs)

    return wrapper
