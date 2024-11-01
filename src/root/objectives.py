from __future__ import annotations

import asyncio
from functools import partial
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Iterator, List, Optional, cast

from root.generated.openapi_aclient.api.objectives_api import ObjectivesApi
from root.generated.openapi_aclient.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest,
)
from root.generated.openapi_aclient.models.objective import Objective as OpenApiObjective
from root.generated.openapi_aclient.models.objective_execution_request import (
    ObjectiveExecutionRequest,
)
from root.generated.openapi_aclient.models.objective_list import ObjectiveList
from root.generated.openapi_aclient.models.objective_request import ObjectiveRequest
from root.generated.openapi_aclient.models.paginated_objective_list import PaginatedObjectiveList
from root.generated.openapi_aclient.models.patched_objective_request import (
    PatchedObjectiveRequest,
)
from root.generated.openapi_aclient.models.validator_execution_result import (
    ValidatorExecutionResult,
)

from .generated.openapi_aclient import ApiClient
from .skills import Skills
from .utils import iterate_cursor_list, wrap_async_iter

if TYPE_CHECKING:
    from .validators import Validator


class Versions:
    """Version listing (sub)API

    Note that this should not be directly instantiated.
    """

    def __init__(self, client: Awaitable[ApiClient]):
        self._client = client

    def list(self, objective_id: str) -> PaginatedObjectiveList:
        """Synchronously list all versions of an objective.

        Args:
          objective_id: The objective to list the versions for
        """
        return asyncio.run(self.alist(objective_id))

    async def alist(self, objective_id: str) -> PaginatedObjectiveList:
        """Asynchronously list all versions of an objective.

        Args:
          objective_id: The objective to list the versions for
        """
        api_instance = ObjectivesApi(await self._client())  # type: ignore[operator]
        return await api_instance.get_a_list_of_all_versions_of_an_objective(id=objective_id)


class Objective(OpenApiObjective):
    """Wrapper for a single Objective.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[ApiClient]

    @classmethod
    def _wrap(cls, apiobj: OpenApiObjective, client: Awaitable[ApiClient]) -> "Objective":
        return asyncio.run(cls._awrap(apiobj, client))

    @classmethod
    async def _awrap(cls, apiobj: OpenApiObjective, client: Awaitable[ApiClient]) -> "Objective":
        if not isinstance(apiobj, OpenApiObjective):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(Objective, apiobj)
        obj.__class__ = cls
        obj._client = client
        return obj

    def run(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Synchronously run all validators associated with the objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """
        return asyncio.run(
            self.arun(
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                _request_timeout=_request_timeout,
            )
        )

    async def arun(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Asynchronously run all validators associated with the objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """
        api_instance = ObjectivesApi(await self._client())  # type: ignore[operator]
        skill_execution_request = ObjectiveExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return await api_instance.objectives_objectives_execute_create(
            objective_id=self.id,
            objective_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )


class Objectives:
    """Objectives API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: Awaitable[ApiClient]):
        self.client = client
        self.versions = Versions(client)

    def create(
        self,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[Validator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """Synchronously create a new objective and return its ID.

        Args:

          intent: The intent of the objective.

          validators: An optional list of validators.

          test_dataset_id: The ID of the test dataset

        """
        return asyncio.run(
            self.acreate(
                intent=intent,
                validators=validators,
                test_dataset_id=test_dataset_id,
                _request_timeout=_request_timeout,
            )
        )

    async def acreate(
        self,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[Validator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """Asynchronously create a new objective and return its ID.

        Args:

          intent: The intent of the objective.

          validators: An optional list of validators.

          test_dataset_id: The ID of the test dataset

        """

        skills = Skills(self.client)
        request = ObjectiveRequest(
            intent=intent,
            validators=[
                await validator._to_request(skills) for validator in validators or []
            ],  # ovdjer unutra ima poziv na skill.list endpoint pa pripazit
            test_dataset_id=test_dataset_id,
        )
        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        objective = await api_instance.objectives_create(objective_request=request)
        return await self.aget(objective.id, _request_timeout=_request_timeout)

    def get(
        self,
        objective_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """
        Synchronously get an objective by ID.

        Args:

          objective_id: The objective to be fetched.

        """
        return asyncio.run(self.aget(objective_id, _request_timeout=_request_timeout))

    async def aget(
        self,
        objective_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """
        Asynchronously get an objective by ID.

        Args:

          objective_id: The objective to be fetched.

        """

        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        return await Objective._awrap(
            await api_instance.objectives_retrieve(id=objective_id, _request_timeout=_request_timeout),
            self.client,
        )

    def delete(self, objective_id: str, *, _request_timeout: Optional[int] = None) -> None:
        """
        Synchronously delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """
        return asyncio.run(self.adelete(objective_id=objective_id, _request_timeout=_request_timeout))

    async def adelete(self, objective_id: str, *, _request_timeout: Optional[int] = None) -> None:
        """
        Asynchronously delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """
        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        return await api_instance.objectives_destroy(id=objective_id, _request_timeout=_request_timeout)

    def list(self, *, intent: Optional[str] = None, limit: int = 100) -> Iterator[ObjectiveList]:
        """Synchronously iterate through the objectives.

        Note:

          The call will list only publicly available global objectives and
          those objectives available to the organzation(s) of the user.

        Args:
          intent: Specific intent the returned objectives must match.
          limit: Number of entries to iterate through at most.

        """
        yield from wrap_async_iter(self.alist(intent=intent, limit=limit))

    async def alist(self, *, intent: Optional[str] = None, limit: int = 100) -> AsyncIterator[ObjectiveList]:
        """Asynchronously iterate through the objectives.

        Note:

          The call will list only publicly available global objectives and
          those objectives available to the organzation(s) of the user.

        Args:
          intent: Specific intent the returned objectives must match.
          limit: Number of entries to iterate through at most.

        """
        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        yield iterate_cursor_list(  # type: ignore[misc]
            partial(api_instance.objectives_list, intent=intent), limit=limit
        )

    def run(
        self,
        objective_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Synchronously run all validators associated with an objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators


        """
        return asyncio.run(
            self.arun(
                objective_id=objective_id,
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                _request_timeout=_request_timeout,
            )
        )

    async def arun(
        self,
        objective_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Asynchronously run all validators associated with an objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators


        """
        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        skill_execution_request = ObjectiveExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return await api_instance.objectives_objectives_execute_create(
            objective_id=objective_id,
            objective_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )

    def update(
        self,
        objective_id: str,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[Validator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """
        Synchronously update an existing objective.

        Args:

          objective_id: The objective to be updated.

          intent: The intent of the objective.

          validators: An optional list of validators.
        """

        return asyncio.run(
            self.aupdate(
                objective_id=objective_id,
                intent=intent,
                validators=validators,
                test_dataset_id=test_dataset_id,
                _request_timeout=_request_timeout,
            )
        )

    async def aupdate(
        self,
        objective_id: str,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[Validator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """
        Asynchronously update an existing objective.

        Args:

          objective_id: The objective to be updated.

          intent: The intent of the objective.

          validators: An optional list of validators.
        """

        skills = Skills(self.client)
        request = PatchedObjectiveRequest(
            intent=intent,
            validators=[await validator._to_request(skills) for validator in validators] if validators else None,
            test_dataset_id=test_dataset_id,
        )
        api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
        return await Objective._awrap(
            await api_instance.objectives_partial_update(
                id=objective_id,
                patched_objective_request=request,
                _request_timeout=_request_timeout,
            ),
            client=self.client,
        )
