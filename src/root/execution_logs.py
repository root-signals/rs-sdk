from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Iterator, Optional, Protocol

from pydantic import StrictStr

from root.generated.openapi_aclient.api.execution_logs_api import ExecutionLogsApi
from root.generated.openapi_aclient.models.execution_log_details import ExecutionLogDetails
from root.generated.openapi_aclient.models.execution_log_list import ExecutionLogList
from root.generated.openapi_aclient.models.paginated_execution_log_list_list import (
    PaginatedExecutionLogListList,
)

from .generated.openapi_aclient import ApiClient
from .utils import wrap_async_iter

if TYPE_CHECKING:

    class ExecutionResult(Protocol):
        execution_log_id: str


class ExecutionLogs:
    """Execution logs API"""

    def __init__(self, client: Awaitable[ApiClient]):
        self._client = client

    def list(
        self,
        *,
        limit: int = 100,
        search_term: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Iterator[ExecutionLogList]:
        """Synchronously list execution logs

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned logs. For example, a skill id or name.
        """
        yield from wrap_async_iter(self.alist(limit=limit, search_term=search_term, _request_timeout=_request_timeout))

    async def alist(
        self,
        *,
        limit: int = 100,
        search_term: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> AsyncIterator[ExecutionLogList]:
        """Asynchronously list execution logs

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned logs. For example, a skill id or name.
        """
        api_instance = ExecutionLogsApi(await self._client())  # type: ignore[operator]
        partial_list = partial(
            api_instance.execution_logs_list,
            search=search_term,
            _request_timeout=_request_timeout,
        )

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: PaginatedExecutionLogListList = await partial_list(page_size=limit, cursor=cursor)
            if not result.results:
                return

            used_results = result.results[:limit]
            for used_result in used_results:
                yield used_result

                limit -= len(used_results)
                if not (cursor := result.next):
                    return

    def get(
        self,
        *,
        log_id: Optional[str] = None,
        execution_result: Optional[ExecutionResult] = None,
        _request_timeout: Optional[int] = None,
    ) -> ExecutionLogDetails:
        """Synchronously get a specific execution log details

        Args:
          log_id: The log to be fetched
          execution_result: The execution result containing the log ID.

        Raises:
          ValueError: If both log_id and execution_result are None.
        """

        return asyncio.run(
            self.aget(log_id=log_id, execution_result=execution_result, _request_timeout=_request_timeout)
        )

    async def aget(
        self,
        *,
        log_id: Optional[str] = None,
        execution_result: Optional[ExecutionResult] = None,
        _request_timeout: Optional[int] = None,
    ) -> ExecutionLogDetails:
        """Asynchronously get a specific execution log details

        Args:
          log_id: The log to be fetched
          execution_result: The execution result containing the log ID.

        Raises:
          ValueError: If both log_id and execution_result are None.
        """

        api_instance = ExecutionLogsApi(await self._client())  # type: ignore[operator]
        _log_id = execution_result.execution_log_id if execution_result else log_id
        if _log_id is None:
            raise ValueError("Either log_id or execution_result must be provided")
        return await api_instance.execution_logs_retrieve(_log_id, _request_timeout=_request_timeout)
