from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Iterator, Optional, Protocol, Union

from pydantic import StrictStr

from .generated.openapi_aclient import ApiClient as AApiClient
from .generated.openapi_aclient.api.execution_logs_api import ExecutionLogsApi as AExecutionLogsApi
from .generated.openapi_aclient.models.execution_log_details import ExecutionLogDetails as AExecutionLogDetails
from .generated.openapi_aclient.models.execution_log_list import ExecutionLogList as AExecutionLogList
from .generated.openapi_aclient.models.paginated_execution_log_list_list import (
    PaginatedExecutionLogListList as APaginatedExecutionLogListList,
)
from .generated.openapi_client import ApiClient
from .generated.openapi_client.api.execution_logs_api import ExecutionLogsApi
from .generated.openapi_client.models.execution_log_details import ExecutionLogDetails
from .generated.openapi_client.models.execution_log_list import ExecutionLogList
from .utils import iterate_cursor_list

if TYPE_CHECKING:

    class ExecutionResult(Protocol):
        execution_log_id: str


class ExecutionLogs:
    """Execution logs API"""

    def __init__(self, client: Union[Awaitable[AApiClient], ApiClient]):
        self._client = client

    def list(
        self,
        *,
        limit: int = 100,
        search_term: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Iterator[ExecutionLogList]:
        """List execution logs

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned logs. For example, a skill id or name.
        """

        if not isinstance(self._client, ApiClient) and self._client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ExecutionLogsApi(self._client)
        yield from iterate_cursor_list(
            partial(
                api_instance.execution_logs_list,
                search=search_term,
                _request_timeout=_request_timeout,
            ),
            limit=limit,
        )

    async def alist(
        self,
        *,
        limit: int = 100,
        search_term: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> AsyncIterator[AExecutionLogList]:
        """Asynchronously list execution logs

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned logs. For example, a skill id or name.
        """

        if self._client is ApiClient:
            raise Exception("This method is not available in synchronous mode")

        api_instance = AExecutionLogsApi(await self._client())  # type: ignore[operator]
        partial_list = partial(
            api_instance.execution_logs_list,
            search=search_term,
            _request_timeout=_request_timeout,
        )

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: APaginatedExecutionLogListList = await partial_list(page_size=limit, cursor=cursor)
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
        """Get a specific execution log details

        Args:
          log_id: The log to be fetched
          execution_result: The execution result containing the log ID.

        Raises:
          ValueError: If both log_id and execution_result are None.
        """

        if not isinstance(self._client, ApiClient) and self._client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ExecutionLogsApi(self._client)
        _log_id = execution_result.execution_log_id if execution_result else log_id
        if _log_id is None:
            raise ValueError("Either log_id or execution_result must be provided")
        return api_instance.execution_logs_retrieve(_log_id, _request_timeout=_request_timeout)

    async def aget(
        self,
        *,
        log_id: Optional[str] = None,
        execution_result: Optional[ExecutionResult] = None,
        _request_timeout: Optional[int] = None,
    ) -> AExecutionLogDetails:
        """Asynchronously get a specific execution log details

        Args:
          log_id: The log to be fetched
          execution_result: The execution result containing the log ID.

        Raises:
          ValueError: If both log_id and execution_result are None.
        """

        if self._client is ApiClient:
            raise Exception("This method is not available in synchronous mode")

        api_instance = AExecutionLogsApi(await self._client())  # type: ignore[operator]
        _log_id = execution_result.execution_log_id if execution_result else log_id
        if _log_id is None:
            raise ValueError("Either log_id or execution_result must be provided")
        return await api_instance.execution_logs_retrieve(_log_id, _request_timeout=_request_timeout)
