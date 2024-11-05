from dataclasses import dataclass
from itertools import chain
from typing import List, Optional

import pytest

from src.root.utils import iterate_cursor_list, wrap_async_iter


@pytest.mark.asyncio
async def test_iterate_cursor_list():
    test_data = list(range(1000))

    @dataclass
    class DummyPaginationResult:
        next: Optional[str]
        results: List[int]

    calls = 0
    page_size_max = 42

    async def dummy_partial(*, cursor, page_size):
        nonlocal calls
        calls += 1
        index = 0
        page_size = min(page_size_max, page_size)
        if cursor:
            index = int(cursor[1:])
        next_cursor = None
        next_index = index + page_size
        if next_index < len(test_data):
            next_cursor = "x" + str(next_index)
        return DummyPaginationResult(next=next_cursor, results=test_data[index:next_index])

    assert next(wrap_async_iter(iterate_cursor_list(dummy_partial, limit=0)), []) == test_data[:0]
    assert calls == 0

    assert next(wrap_async_iter(iterate_cursor_list(dummy_partial, limit=12))) == test_data[:12]
    assert calls == 1

    # Ensure that page size aligned fetches still call backend only correct number of times
    calls = 0
    limit = page_size_max * 2
    assert (
        list(chain.from_iterable(wrap_async_iter(iterate_cursor_list(dummy_partial, limit=limit)))) == test_data[:limit]
    )
    assert calls == 2

    # Ensure that those that do not align make the extra fetch for partials
    calls = 0
    limit = 123
    assert (
        list(chain.from_iterable(wrap_async_iter(iterate_cursor_list(dummy_partial, limit=limit)))) == test_data[:limit]
    )
    assert calls == limit // page_size_max + 1

    # Ensure that getting more than what is available works correctly too
    calls = 0
    assert list(chain.from_iterable(wrap_async_iter(iterate_cursor_list(dummy_partial, limit=1234)))) == test_data
    assert calls == 1000 // page_size_max + 1
