from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Iterator, List, Optional, Union, cast

from pydantic import StrictStr

from .generated.openapi_aclient import ApiClient as AApiClient
from .generated.openapi_aclient.api.objectives_api import ObjectivesApi as AObjectivesApi
from .generated.openapi_aclient.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest as AEvaluatorExecutionFunctionsRequest,
)
from .generated.openapi_aclient.models.objective import Objective as AOpenApiObjective
from .generated.openapi_aclient.models.objective_execution_request import (
    ObjectiveExecutionRequest as AObjectiveExecutionRequest,
)
from .generated.openapi_aclient.models.objective_list import ObjectiveList as AObjectiveList
from .generated.openapi_aclient.models.objective_request import ObjectiveRequest as AObjectiveRequest
from .generated.openapi_aclient.models.paginated_objective_list import (
    PaginatedObjectiveList as APaginatedObjectiveList,
)
from .generated.openapi_aclient.models.paginated_objective_list_list import (
    PaginatedObjectiveListList as APaginatedObjectiveListList,
)
from .generated.openapi_aclient.models.patched_objective_request import (
    PatchedObjectiveRequest as APatchedObjectiveRequest,
)
from .generated.openapi_aclient.models.validator_execution_result import (
    ValidatorExecutionResult as AValidatorExecutionResult,
)
from .generated.openapi_client import ApiClient
from .generated.openapi_client.api.objectives_api import ObjectivesApi
from .generated.openapi_client.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest,
)
from .generated.openapi_client.models.objective import Objective as OpenApiObjective
from .generated.openapi_client.models.objective_execution_request import ObjectiveExecutionRequest
from .generated.openapi_client.models.objective_list import ObjectiveList
from .generated.openapi_client.models.objective_request import ObjectiveRequest
from .generated.openapi_client.models.paginated_objective_list import PaginatedObjectiveList
from .generated.openapi_client.models.patched_objective_request import PatchedObjectiveRequest
from .generated.openapi_client.models.validator_execution_result import ValidatorExecutionResult
from .skills import Skills
from .utils import iterate_cursor_list
from .validators import AValidator

if TYPE_CHECKING:
    from .validators import Validator


class Versions:
    """Version listing (sub)API

    Note that this should not be directly instantiated.
    """

    def __init__(self, client: Union[Awaitable[AApiClient], ApiClient]):
        self._client = client

    def list(self, objective_id: str) -> PaginatedObjectiveList:
        """List all versions of an objective.

        Args:
          objective_id: The objective to list the versions for
        """

        if not isinstance(self._client, ApiClient) and self._client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ObjectivesApi(self._client)
        return api_instance.get_a_list_of_all_versions_of_an_objective(id=objective_id)

    async def alist(self, objective_id: str) -> APaginatedObjectiveList:
        """Asynchronously list all versions of an objective.

        Args:
          objective_id: The objective to list the versions for
        """

        if self._client is ApiClient:
            raise Exception("This method is not available in synchronous mode")

        api_instance = AObjectivesApi(await self._client())  # type: ignore[operator]
        return await api_instance.get_a_list_of_all_versions_of_an_objective(id=objective_id)


class Objective(OpenApiObjective):
    """Wrapper for a single Objective.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: ApiClient

    @classmethod
    def _wrap(cls, apiobj: OpenApiObjective, client: ApiClient) -> "Objective":
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
        Run all validators associated with the objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """

        api_instance = ObjectivesApi(self._client)
        skill_execution_request = ObjectiveExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return api_instance.objectives_objectives_execute_create(
            objective_id=self.id,
            objective_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )


class AObjective(AOpenApiObjective):
    """Wrapper for a single Objective.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[AApiClient]

    @classmethod
    async def _awrap(cls, apiobj: AOpenApiObjective, client: Awaitable[AApiClient]) -> "AObjective":
        if not isinstance(apiobj, AOpenApiObjective):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(AObjective, apiobj)
        obj.__class__ = cls
        obj._client = client
        return obj

    async def arun(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[AEvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> AValidatorExecutionResult:
        """
        Asynchronously run all validators associated with the objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """

        api_instance = AObjectivesApi(await self._client())  # type: ignore[operator]
        skill_execution_request = AObjectiveExecutionRequest(
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

    def __init__(self, client: Union[Awaitable[AApiClient], ApiClient]):
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
        """Create a new objective and return its ID.

        Args:

          intent: The intent of the objective.

          validators: An optional list of validators.

          test_dataset_id: The ID of the test dataset

        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        skills = Skills(self.client)
        request = ObjectiveRequest(
            intent=intent,
            validators=[validator._to_request(skills) for validator in validators or []],
            test_dataset_id=test_dataset_id,
        )
        api_instance = ObjectivesApi(self.client)
        objective = api_instance.objectives_create(objective_request=request)
        return self.get(objective.id, _request_timeout=_request_timeout)

    async def acreate(
        self,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[AValidator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> AObjective:
        """Asynchronously create a new objective and return its ID.

        Args:

          intent: The intent of the objective.

          validators: An optional list of validators.

          test_dataset_id: The ID of the test dataset

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        skills = Skills(self.client)
        request = AObjectiveRequest(
            intent=intent,
            validators=[await avalidator._ato_request(skills) for avalidator in validators or []],
            test_dataset_id=test_dataset_id,
        )
        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        objective = await api_instance.objectives_create(objective_request=request)
        return await self.aget(objective.id, _request_timeout=_request_timeout)

    def get(
        self,
        objective_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> Objective:
        """
        Get an objective by ID.

        Args:

          objective_id: The objective to be fetched.

        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ObjectivesApi(self.client)
        return Objective._wrap(
            api_instance.objectives_retrieve(id=objective_id, _request_timeout=_request_timeout),
            self.client,  # type: ignore[arg-type]
        )

    async def aget(
        self,
        objective_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> AObjective:
        """
        Asynchronously get an objective by ID.

        Args:

          objective_id: The objective to be fetched.

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        return await AObjective._awrap(
            await api_instance.objectives_retrieve(id=objective_id, _request_timeout=_request_timeout),
            self.client,
        )

    def delete(self, objective_id: str, *, _request_timeout: Optional[int] = None) -> None:
        """
        Delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ObjectivesApi(self.client)
        return api_instance.objectives_destroy(id=objective_id, _request_timeout=_request_timeout)

    async def adelete(self, objective_id: str, *, _request_timeout: Optional[int] = None) -> None:
        """
        Asynchronously delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        return await api_instance.objectives_destroy(id=objective_id, _request_timeout=_request_timeout)

    def list(self, *, intent: Optional[str] = None, limit: int = 100) -> Iterator[ObjectiveList]:
        """Iterate through the objectives.

        Note:

          The call will list only publicly available global objectives and
          those objectives available to the organzation(s) of the user.

        Args:
          intent: Specific intent the returned objectives must match.
          limit: Number of entries to iterate through at most.

        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ObjectivesApi(self.client)
        yield from iterate_cursor_list(partial(api_instance.objectives_list, intent=intent), limit=limit)

    async def alist(self, *, intent: Optional[str] = None, limit: int = 100) -> AsyncIterator[AObjectiveList]:
        """Asynchronously iterate through the objectives.

        Note:

          The call will list only publicly available global objectives and
          those objectives available to the organzation(s) of the user.

        Args:
          intent: Specific intent the returned objectives must match.
          limit: Number of entries to iterate through at most.

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        partial_list = partial(api_instance.objectives_list, intent=intent)

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: APaginatedObjectiveListList = await partial_list(page_size=limit, cursor=cursor)
            if not result.results:
                return

            used_results = result.results[:limit]
            for used_result in used_results:
                yield used_result

                limit -= len(used_results)
                if not (cursor := result.next):
                    return

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
        Run all validators associated with an objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        api_instance = ObjectivesApi(self.client)
        skill_execution_request = ObjectiveExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return api_instance.objectives_objectives_execute_create(
            objective_id=objective_id,
            objective_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )

    async def arun(
        self,
        objective_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[AEvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> AValidatorExecutionResult:
        """
        Asynchronously run all validators associated with an objective.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        skill_execution_request = AObjectiveExecutionRequest(
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
        Update an existing objective.

        Args:

          objective_id: The objective to be updated.

          intent: The intent of the objective.

          validators: An optional list of validators.
        """

        if isinstance(self.client, AApiClient):
            raise Exception("This method is not available in asynchronous mode")

        skills = Skills(self.client)
        request = PatchedObjectiveRequest(
            intent=intent,
            validators=[validator._to_request(skills) for validator in validators] if validators else None,
            test_dataset_id=test_dataset_id,
        )
        api_instance = ObjectivesApi(self.client)
        return Objective._wrap(
            api_instance.objectives_partial_update(
                id=objective_id,
                patched_objective_request=request,
                _request_timeout=_request_timeout,
            ),
            client=self.client,  # type: ignore[arg-type]
        )

    async def aupdate(
        self,
        objective_id: str,
        *,
        intent: Optional[str] = None,
        validators: Optional[List[AValidator]] = None,
        test_dataset_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> AObjective:
        """
        Asynchronously update an existing objective.

        Args:

          objective_id: The objective to be updated.

          intent: The intent of the objective.

          validators: An optional list of validators.
        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        skills = Skills(self.client)
        request = APatchedObjectiveRequest(
            intent=intent,
            validators=[await validator._ato_request(skills) for validator in validators] if validators else None,
            test_dataset_id=test_dataset_id,
        )
        api_instance = AObjectivesApi(await self.client())  # type: ignore[operator]
        return await AObjective._awrap(
            await api_instance.objectives_partial_update(
                id=objective_id,
                patched_objective_request=request,
                _request_timeout=_request_timeout,
            ),
            client=self.client,
        )
