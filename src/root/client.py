from __future__ import annotations

import os
import re
import textwrap
from functools import cached_property
from typing import TYPE_CHECKING, Awaitable, Optional, Union

from .__about__ import __version__
from .generated import openapi_aclient, openapi_client
from .generated.openapi_aclient.configuration import Configuration as _AConfiguration
from .generated.openapi_client.configuration import Configuration as _Configuration

if TYPE_CHECKING:
    from .datasets import DataSets
    from .execution_logs import ExecutionLogs
    from .models import Models
    from .objectives import Objectives
    from .skills import Evaluators, Skills


def _get_api_key(*, dot_env: str = ".env") -> str:
    var = "ROOTSIGNALS_API_KEY"
    api_key = os.environ.get(var)
    if api_key is not None:
        return api_key
    if os.path.exists(dot_env):
        for line in open(dot_env):
            m = re.fullmatch(line, rf"^\s*{var}\s*=\s*(\S+)\s*$")
            if m is not None:
                return m.group(1)
    raise ValueError(
        textwrap.dedent("""
    Root Signals API key cannot be found.
    It can be provided in client invocation, using ROOTSIGNALS_API_KEY environment variable or .env file line
    """)
    )


class RootSignals:
    """Root Signals API Python client.

    The API key must be provided via one of the following methods - the code uses the first one that is found:

    1. as an argument to RootSignals constructor    ,
    2. environment variable `ROOTSIGNALS_API_KEY`, or
    3. .env file containing `ROOTSIGNALS_API_KEY=`

    Args:
        api_key: Root Signals API Key (if not provided from environment)
        base_url: Root Signals base URL to use (default is fine)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        run_async: bool = False,
        _api_client: Union[Optional[Awaitable[openapi_aclient.ApiClient]], Optional[openapi_client.ApiClient]] = None,
    ):
        self.run_async = run_async
        if api_key is None:
            api_key = _get_api_key()
        if base_url is None:
            base_url = os.environ.get("ROOTSIGNALS_API_URL", "https://api.app.rootsignals.ai")
        self.base_url = base_url
        self.api_key = api_key
        self._api_client_arg = _api_client

    @cached_property
    def get_api_client(self) -> Union[openapi_client.ApiClient, openapi_aclient.ApiClient]:
        if self._api_client_arg is not None:
            return self._api_client_arg  # type: ignore[return-value]

        if self.run_async:
            return self._aapi_client  # type: ignore[return-value]

        return self._api_client

    @property
    def _api_client(self) -> openapi_client.ApiClient:
        """Get the OpenAPI client

        End users should not need to inheract with OpenAPI directly.

        Note that this call is cached for duration of the RootSignals
        instance; later calls will return the same instance.
        """

        api_client_configuration = _Configuration(host=self.base_url)
        api_client_configuration.api_key["publicApiKey"] = f"Api-Key {self.api_key}"
        return openapi_client.ApiClient(
            api_client_configuration, header_name="x-root-python-version", header_value=__version__
        )

    async def _aapi_client(self) -> openapi_aclient.ApiClient:
        """Get the OpenAPI client

        End users should not need to inheract with OpenAPI directly.

        Note that this call is cached for duration of the RootSignals
        instance; later calls will return the same instance.
        """

        api_client_configuration = _AConfiguration(host=self.base_url)
        api_client_configuration.api_key["publicApiKey"] = f"Api-Key {self.api_key}"

        return openapi_aclient.ApiClient(
            api_client_configuration, header_name="x-root-python-version", header_value=__version__
        )

    @cached_property
    def datasets(self) -> DataSets:
        """Get DataSets API"""

        from .datasets import DataSets

        return DataSets(self.get_api_client, self.base_url, self.api_key)  # type: ignore[arg-type]

    @cached_property
    def evaluators(self) -> Evaluators:
        """Get Evaluators API"""

        from .skills import Evaluators

        return Evaluators(self.get_api_client)  # type: ignore[arg-type]

    @cached_property
    def execution_logs(self) -> ExecutionLogs:
        """Get Execution Logs API"""
        from .execution_logs import ExecutionLogs

        return ExecutionLogs(self.get_api_client)  # type: ignore[arg-type]

    @cached_property
    def models(self) -> Models:
        """Get Models API"""
        from .models import Models

        return Models(self.get_api_client)  # type: ignore[arg-type]

    @cached_property
    def objectives(self) -> Objectives:
        """Get Objectives API"""
        from .objectives import Objectives

        return Objectives(self.get_api_client)  # type: ignore[arg-type]

    @cached_property
    def skills(self) -> Skills:
        """Get Skills API"""
        from .skills import Skills

        return Skills(self.get_api_client)  # type: ignore[arg-type]
