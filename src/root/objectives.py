from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Iterator, List, Optional, cast

from root.generated.openapi_client.api.objectives_api import ObjectivesApi
from root.generated.openapi_client.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest,
)
from root.generated.openapi_client.models.objective import Objective as OpenApiObjective
from root.generated.openapi_client.models.objective_execution_request import (
    ObjectiveExecutionRequest,
)
from root.generated.openapi_client.models.objective_list import ObjectiveList
from root.generated.openapi_client.models.objective_request import ObjectiveRequest
from root.generated.openapi_client.models.paginated_objective_list import PaginatedObjectiveList
from root.generated.openapi_client.models.patched_objective_request import (
    PatchedObjectiveRequest,
)
from root.generated.openapi_client.models.validator_execution_result import (
    ValidatorExecutionResult,
)

from .generated.openapi_client import ApiClient
from .skills import Skills
from .utils import iterate_cursor_list

if TYPE_CHECKING:
    from .validators import Validator


class Versions:
    """Version listing (sub)API

    Note that this should not be directly instantiated.
    """

    def __init__(self, client: ApiClient):
        self._client = client

    def list(self, objective_id: str) -> PaginatedObjectiveList:
        """List all versions of an objective.

        Args:
          objective_id: The objective to list the versions for
        """
        api_instance = ObjectivesApi(self._client)
        return api_instance.get_a_list_of_all_versions_of_an_objective(id=objective_id)


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


class Objectives:
    """Objectives API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient):
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
        skills = Skills(self.client)
        request = ObjectiveRequest(
            intent=intent,
            validators=[validator._to_request(skills) for validator in validators or []],
            test_dataset_id=test_dataset_id,
        )
        api_instance = ObjectivesApi(self.client)
        objective = api_instance.objectives_create(objective_request=request)
        return self.get(objective.id, _request_timeout=_request_timeout)

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
        api_instance = ObjectivesApi(self.client)
        return Objective._wrap(
            api_instance.objectives_retrieve(id=objective_id, _request_timeout=_request_timeout),
            self.client,
        )

    def delete(self, objective_id: str, *, _request_timeout: Optional[int] = None) -> None:
        """
        Delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """
        api_instance = ObjectivesApi(self.client)
        return api_instance.objectives_destroy(id=objective_id, _request_timeout=_request_timeout)

    def list(self, *, intent: Optional[str] = None, limit: int = 100) -> Iterator[ObjectiveList]:
        """Iterate through the objectives.

        Note:

          The call will list only publicly available global objectives and
          those objectives available to the organzation(s) of the user.

        Args:
          intent: Specific intent the returned objectives must match.
          limit: Number of entries to iterate through at most.

        """
        api_instance = ObjectivesApi(self.client)
        yield from iterate_cursor_list(partial(api_instance.objectives_list, intent=intent), limit=limit)

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
            client=self.client,
        )
