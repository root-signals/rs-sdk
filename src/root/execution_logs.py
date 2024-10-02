from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Iterator, Optional, Protocol

from root.generated.openapi_client.api.execution_logs_api import ExecutionLogsApi
from root.generated.openapi_client.models.execution_log_details import ExecutionLogDetails
from root.generated.openapi_client.models.execution_log_list import ExecutionLogList

from .generated.openapi_client import ApiClient
from .utils import iterate_cursor_list

if TYPE_CHECKING:

    class ExecutionResult(Protocol):
        execution_log_id: str


class ExecutionLogs:
    """Execution logs API"""

    def __init__(self, client: ApiClient):
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
        api_instance = ExecutionLogsApi(self._client)
        yield from iterate_cursor_list(
            partial(
                api_instance.execution_logs_list,
                search=search_term,
                _request_timeout=_request_timeout,
            ),
            limit=limit,
        )

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

        api_instance = ExecutionLogsApi(self._client)
        _log_id = execution_result.execution_log_id if execution_result else log_id
        if _log_id is None:
            raise ValueError("Either log_id or execution_result must be provided")
        return api_instance.execution_logs_retrieve(_log_id, _request_timeout=_request_timeout)
