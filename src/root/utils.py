from typing import Any, Generic, Iterator, List, Optional, TypeVar

from pydantic import StrictStr

T = TypeVar("T")


# This is internal generic class only to handle duck typing of the
# local codes' correctness.
#
# The original classes returned by partial_list may or may not have
# anything to do with this (in practise they are pydantic BaseModel
# subclasses that have no shared superclass unfortunately).
class _PartialResult(Generic[T]):
    next: Optional[StrictStr] = None
    results: Optional[List[T]] = None


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
