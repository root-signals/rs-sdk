from __future__ import annotations

import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from typing import TYPE_CHECKING, Dict, Iterator, List, Literal, Optional, Union, cast

from pydantic import BaseModel

from root.generated.openapi_client.api.chats_api import ChatsApi
from root.generated.openapi_client.api.skills_api import SkillsApi
from root.generated.openapi_client.models.chat_create_request import ChatCreateRequest
from root.generated.openapi_client.models.data_loader_request import DataLoaderRequest
from root.generated.openapi_client.models.input_variable_request import InputVariableRequest
from root.generated.openapi_client.models.objective_request import ObjectiveRequest
from root.generated.openapi_client.models.paginated_skill_list import PaginatedSkillList
from root.generated.openapi_client.models.patched_skill_request import PatchedSkillRequest
from root.generated.openapi_client.models.reference_variable_request import ReferenceVariableRequest
from root.generated.openapi_client.models.skill import Skill as OpenAPISkill
from root.generated.openapi_client.models.skill_execution_request import SkillExecutionRequest
from root.generated.openapi_client.models.skill_execution_result import SkillExecutionResult
from root.generated.openapi_client.models.skill_list_output import SkillListOutput
from root.generated.openapi_client.models.skill_request import SkillRequest
from root.generated.openapi_client.models.skill_test_data_request import SkillTestDataRequest
from root.generated.openapi_client.models.skill_test_input_request import SkillTestInputRequest
from root.generated.openapi_client.models.skill_test_output import SkillTestOutput
from root.generated.openapi_client.models.skill_validator_execution_request import (
    SkillValidatorExecutionRequest,
)
from root.generated.openapi_client.models.validator_execution_result import (
    ValidatorExecutionResult,
)

from .data_loader import DataLoader
from .generated.openapi_client import ApiClient
from .generated.openapi_client.models import (
    EvaluatorDemonstrationsRequest,
    EvaluatorExecutionFunctionsRequest,
    EvaluatorExecutionRequest,
    EvaluatorExecutionResult,
    ModelParamsRequest,
)
from .skill_chat import SkillChat
from .utils import iterate_cursor_list

if TYPE_CHECKING:
    from .validators import Validator


ModelName = Union[
    str,
    Literal[
        "root",  # RS-chosen model
    ],
]


class ModelParams(BaseModel):
    """Additional model parameters.

    All fields are made optional in practice.
    """

    temperature: Optional[float] = None


class ReferenceVariable(BaseModel):
    """Reference variable definition.

    `name` within prompt gets populated with content from `dataset_id`.
    """

    name: str
    dataset_id: str


class InputVariable(BaseModel):
    """Input variable definition.

    `name` within prompt gets populated with the provided variable.
    """

    name: str


class EvaluatorDemonstration(BaseModel):
    """Evaluator demonstration

    Demonstrations are used to train an evaluator to adjust its behavior.
    """

    prompt: Optional[str] = None
    output: str
    score: float
    justification: Optional[str] = None


class CalibrateBatchParameters:
    def __init__(
        self,
        name: str,
        prompt: str,
        model: "ModelName",
        pii_filter: bool = False,
        reference_variables: Optional[Union[List["ReferenceVariable"], List["ReferenceVariableRequest"]]] = None,
        input_variables: Optional[Union[List["InputVariable"], List["InputVariableRequest"]]] = None,
        data_loaders: Optional[List["DataLoader"]] = None,
    ):
        self.name = name
        self.prompt = prompt
        self.model = model
        self.pii_filter = pii_filter
        self.reference_variables = reference_variables
        self.input_variables = input_variables
        self.data_loaders = data_loaders


class CalibrateBatchResult(BaseModel):
    results: List[SkillTestOutput]
    rms_errors_model: Dict[str, float]
    mae_errors_model: Dict[str, float]
    rms_errors_prompt: Dict[str, float]
    mae_errors_prompt: Dict[str, float]


class Versions:
    """Version listing (sub)API

    Note that this should not be directly instantiated.
    """

    def __init__(self, client: ApiClient):
        self._client = client

    def list(self, skill_id: str) -> PaginatedSkillList:
        """List all versions of a skill.

        Args:
          skill_id: The skill to list the versions for
        """
        api_instance = SkillsApi(self._client)
        return api_instance.get_a_list_of_all_versions_of_a_skill(id=skill_id)


class Skill(OpenAPISkill):
    """Wrapper for a single Skill.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: ApiClient

    @classmethod
    def _wrap(cls, apiobj: OpenAPISkill, client: ApiClient) -> "Skill":
        if not isinstance(apiobj, OpenAPISkill):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(Skill, apiobj)
        obj.__class__ = cls
        obj._client = client
        return obj

    @property
    def openai_base_url(self) -> str:
        """Get the OpenAI compatibility API URL for the skill.

        Currently only OpenAI chat completions API is supported using
        the base URL.
        """
        return f"{self._client.configuration._base_path}/skills/openai/{self.id}"

    def run(self, variables: Optional[Dict[str, str]] = None) -> SkillExecutionResult:
        """Run a skill with optional variables.

        Args:
          variables: The variables to be provided to the skill.
        """
        api_instance = SkillsApi(self._client)
        skill_execution_request = SkillExecutionRequest(
            variables=variables,
            skill_version_id=None,
        )
        return api_instance.skills_execute_create(id=self.id, skill_execution_request=skill_execution_request)

    def evaluate(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
    ) -> ValidatorExecutionResult:
        """
        Run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """
        api_instance = SkillsApi(self._client)
        skill_execution_request = SkillValidatorExecutionRequest(
            skill_version_id=None,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return api_instance.skills_execute_validators_create(
            id=self.id, skill_validator_execution_request=skill_execution_request
        )


def _to_data_loaders(data_loaders: Optional[List[DataLoader]]) -> List[DataLoaderRequest]:
    return [
        DataLoaderRequest(name=data_loader.name, type=data_loader.type, parameters=data_loader._get_parameter_dict())
        for data_loader in (data_loaders or [])
    ]


def _to_input_variables(
    input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]],
) -> List[InputVariableRequest]:
    def _convert_to_generated_model(entry: Union[InputVariable, InputVariableRequest]) -> InputVariableRequest:
        if not isinstance(entry, InputVariableRequest):
            return InputVariableRequest(name=entry.name)
        return entry

    return [_convert_to_generated_model(entry) for entry in input_variables or {}]


def _to_model_params(model_params: Optional[Union[ModelParams, ModelParamsRequest]]) -> Optional[ModelParamsRequest]:
    if isinstance(model_params, ModelParams):
        return ModelParamsRequest(**model_params.model_dump())
    return model_params


def _to_reference_variables(
    reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]],
) -> List[ReferenceVariableRequest]:
    def _convert_to_generated_model(
        entry: Union[ReferenceVariable, ReferenceVariableRequest],
    ) -> ReferenceVariableRequest:
        if not isinstance(entry, ReferenceVariableRequest):
            return ReferenceVariableRequest(name=entry.name, dataset=entry.dataset_id)
        return entry

    return [_convert_to_generated_model(entry) for entry in reference_variables or {}]


def _to_evaluator_demonstrations(
    input_variables: Optional[Union[List[EvaluatorDemonstration], List[EvaluatorDemonstrationsRequest]]],
) -> List[EvaluatorDemonstrationsRequest]:
    def _convert_dict(
        entry: Union[EvaluatorDemonstration, EvaluatorDemonstrationsRequest],
    ) -> EvaluatorDemonstrationsRequest:
        if not isinstance(entry, EvaluatorDemonstrationsRequest):
            return EvaluatorDemonstrationsRequest(
                score=entry.score,
                prompt=entry.prompt,
                output=entry.output,
                justification=entry.justification,
            )
        return entry

    return [_convert_dict(entry) for entry in input_variables or {}]


class Skills:
    """Skills API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient):
        self.client = client
        self.versions = Versions(client)

    def _to_objective_request(
        self, *, intent: Optional[str] = None, validators: Optional[List[Validator]] = None
    ) -> ObjectiveRequest:
        return ObjectiveRequest(
            intent=intent,
            validators=[validator._to_request(self) for validator in validators or []],
        )

    def create(
        self,
        prompt: str = "",
        *,
        name: Optional[str] = None,
        intent: Optional[str] = None,
        model: Optional[ModelName] = None,
        system_message: str = "",
        fallback_models: Optional[List[ModelName]] = None,
        pii_filter: bool = False,
        validators: Optional[List[Validator]] = None,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        is_evaluator: Optional[bool] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        objective_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> Skill:
        """Create a new skill and return the result

        Args:

          prompt: The prompt that is provided to the model (not used
          if using OpenAI compatibility API)

          name: Name of the skill (defaulting to <unnamed>)

          objective_id: Already created objective id to assign to the skill.

          intent: The intent of the skill (defaulting to name); not available if objective_id is set.

          model: The model to use (defaults to 'root', which means
            Root Signals default at the time of skill creation)

          system_message: The system instruction to give to the model
            (mainly useful with OpenAI compatibility API).

          pii_filter: Whether to use PII filter or not.

          validators: An optional list of validators; not available if objective_id is set.

          reference_variables: An optional list of input variables for
            the skill.

          input_variables: An optional list of reference variables for
            the skill.

          is_evaluator: Whether the skill is an evaluator or
            not. Evaluators should have prompts that cause model to
            return

          data_loaders: An optional list of data loaders, which
            populate the reference variables.

          model_params: An optional set of additional parameters to the model.

          overwrite: Whether to overwrite a skill with the same name if it exists.

        """
        if name is None:
            name = "<unnamed>"
        api_instance = SkillsApi(self.client)
        objective: Optional[ObjectiveRequest] = None
        if objective_id is None:
            if intent is None:
                intent = name
            objective = self._to_objective_request(intent=intent, validators=validators)
        else:
            if intent:
                raise ValueError("Supplying both objective_id and intent is not supported")
            if validators:
                raise ValueError("Supplying both objective_id and validators is not supported")
        skill_request = SkillRequest(
            name=name,
            objective=objective,
            objective_id=objective_id,
            system_message=system_message,
            prompt=prompt,
            models=[model for model in [model] + (fallback_models or []) if model is not None],
            pii_filter=pii_filter,
            is_evaluator=is_evaluator,
            reference_variables=_to_reference_variables(reference_variables),
            input_variables=_to_input_variables(input_variables),
            data_loaders=_to_data_loaders(data_loaders),
            model_params=_to_model_params(model_params),
            overwrite=overwrite,
        )

        skill = api_instance.skills_create(skill_request=skill_request)
        return Skill._wrap(skill, self.client)

    def update(
        self,
        skill_id: str,
        *,
        change_note: Optional[str] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        intent: Optional[str] = None,
        fallback_models: Optional[List[ModelName]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        model: Optional[ModelName] = None,
        name: Optional[str] = None,
        pii_filter: Optional[bool] = None,
        prompt: Optional[str] = None,
        is_evaluator: Optional[bool] = None,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        validators: Optional[List[Validator]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        evaluator_demonstrations: Optional[List[EvaluatorDemonstration]] = None,
    ) -> Skill:
        """Update existing skill instance and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        Args:
          skill_id: The skill to be updated
        """
        api_instance = SkillsApi(self.client)
        request = PatchedSkillRequest(
            name=name,
            objective=self._to_objective_request(intent=intent, validators=validators),
            prompt=prompt,
            models=[model] + (fallback_models or []) if model else None,
            pii_filter=pii_filter,
            is_evaluator=is_evaluator,
            reference_variables=_to_reference_variables(reference_variables),
            input_variables=_to_input_variables(input_variables),
            data_loaders=_to_data_loaders(data_loaders),
            change_note=change_note or "Updated skill from SDK",
            model_params=_to_model_params(model_params),
            evaluator_demonstrations=_to_evaluator_demonstrations(evaluator_demonstrations),
        )
        api_response = api_instance.skills_partial_update(id=skill_id, patched_skill_request=request)
        return Skill._wrap(api_response, self.client)

    def get(self, skill_id: str) -> Skill:
        """Get a Skill instance by ID.

        Args:
          skill_id: The skill to be fetched
        """

        api_instance = SkillsApi(self.client)
        api_response = api_instance.skills_retrieve(id=skill_id)
        return Skill._wrap(api_response, self.client)

    def list(
        self,
        search_term: Optional[str] = None,
        *,
        limit: int = 100,
        name: Optional[str] = None,
        only_evaluators: bool = False,
    ) -> Iterator[SkillListOutput]:
        """Iterate through the skills.

        Note that call will list only publicly available global skills, and
        those models within organization that are available to the current
        user (or all if the user is an admin).

        Args:
          limit: Number of entries to iterate through at most.

          name: Specific name the returned skills must match.

          only_evaluators: Match only Skills with is_evaluator=True.

          search_term: Can be used to limit returned skills.
        """

        api_instance = SkillsApi(self.client)
        yield from iterate_cursor_list(
            partial(
                api_instance.skills_list, name=name, search=search_term, is_evaluator=True if only_evaluators else None
            ),
            limit=limit,
        )

    def test(
        self,
        test_dataset_id: str,
        prompt: str,
        model: ModelName,
        *,
        fallback_models: Optional[List[ModelName]] = None,
        pii_filter: bool = False,
        validators: Optional[List[Validator]] = None,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        data_loaders: Optional[List[DataLoader]] = None,
    ) -> List[SkillTestOutput]:
        """
        Test a skill definition with a test dataset and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        """
        api_instance = SkillsApi(self.client)
        skill_test_request = SkillTestInputRequest(
            test_dataset_id=test_dataset_id,
            prompt=prompt,
            models=[model] + (fallback_models or []),
            pii_filter=pii_filter,
            objective=self._to_objective_request(validators=validators),
            reference_variables=_to_reference_variables(reference_variables),
            input_variables=_to_input_variables(input_variables),
            data_loaders=_to_data_loaders(data_loaders),
        )
        return api_instance.skills_test_create(skill_test_request)

    def test_existing(
        self,
        skill_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
    ) -> List[SkillTestOutput]:
        """
        Test an existing skill.

        Note that only one of the test_data and test_data_set must be provided.

        Args:

          test_data: Actual data to be used to test the skill.

          test_dataset_id: ID of the dataset to be used to test the skill.

        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(self.client)
        skill_test_request = SkillTestDataRequest(
            test_dataset_id=test_dataset_id,
            test_data=test_data,
        )
        return api_instance.skills_test_create2(skill_id, skill_test_request)

    def create_chat(self, skill_id: str, *, chat_id: Optional[str] = None, name: Optional[str] = None) -> SkillChat:
        """
        Create and store chat object with the given parameters.

        Args:

          skill_id: The skill to chat with.

          chat_id: Optional identifier to identify the chat. If not supplied, one is automatically generated.

          name: Optional name for the chat.
        """
        api_instance = ChatsApi(self.client)
        chat_create_request = ChatCreateRequest(
            name=name,
            skill_id=skill_id,
            chat_id=chat_id,
        )
        if chat_id:
            return SkillChat._wrap(
                api_instance.chats_initiate_create2(chat_id=chat_id, chat_create_request=chat_create_request),
                self.client,
            )
        else:
            return SkillChat._wrap(api_instance.chats_initiate_create(chat_create_request), self.client)

    def delete(self, skill_id: str) -> None:
        """
        Delete the skill from the registry.

        Args:

          skill_id: The skill to be deleted.

        """
        api_instance = SkillsApi(self.client)
        return api_instance.skills_destroy(id=skill_id)

    def run(
        self,
        skill_id: str,
        variables: Optional[Dict[str, str]] = None,
        *,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        skill_version_id: Optional[str] = None,
    ) -> SkillExecutionResult:
        """
        Run a skill with optional variables, model parameters, and a skill version id.
        If no skill version id is given, the latest version of the skill will be used.
        If model parameters are not given, Skill model params will be used. If the skill has no model params
        the default model parameters will be used.

        Returns a dictionary with the following keys:
        - llm_output: the LLM response of the skill run
        - validation: the result of the skill validation
        """
        api_instance = SkillsApi(self.client)
        skill_execution_request = SkillExecutionRequest(
            variables=variables,
            skill_version_id=skill_version_id,
            model_params=_to_model_params(model_params),
        )
        return api_instance.skills_execute_create(id=skill_id, skill_execution_request=skill_execution_request)

    def evaluate(
        self,
        skill_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        skill_version_id: Optional[str] = None,
    ) -> ValidatorExecutionResult:
        """
        Run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          skill_version_id: Skill version id. If omitted, the latest version is used.

        """
        api_instance = SkillsApi(self.client)
        skill_execution_request = SkillValidatorExecutionRequest(
            skill_version_id=skill_version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return api_instance.skills_execute_validators_create(
            id=skill_id, skill_validator_execution_request=skill_execution_request
        )


class Evaluators:
    """Evaluators (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient):
        self.client = client
        self.versions = Versions(client)

    def run(
        self,
        evaluator_id: str,
        *,
        request: str,
        response: str,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        evaluator_version_id: Optional[str] = None,
    ) -> EvaluatorExecutionResult:
        """
        Run an evaluator using its id and an optional version id .
        If no evaluator version id is given, the latest version of the evaluator will be used.

        Returns a dictionary with the following keys:
        - score: a value between 0 and 1 representing the score of the evaluator
        """
        api_instance = SkillsApi(self.client)
        evaluator_execution_request = EvaluatorExecutionRequest(
            skill_version_id=evaluator_version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return api_instance.skills_evaluator_execute_create(
            skill_id=evaluator_id,
            evaluator_execution_request=evaluator_execution_request,
        )

    def calibrate_existing(
        self,
        evaluator_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
    ) -> List[SkillTestOutput]:
        """
        Run calibration set on an existing evaluator.
        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(self.client)
        skill_test_request = SkillTestDataRequest(
            test_dataset_id=test_dataset_id,
            test_data=test_data,
        )
        return api_instance.skills_calibrate_create2(evaluator_id, skill_test_request)

    def calibrate(
        self,
        *,
        name: str,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        prompt: str,
        model: ModelName,
        pii_filter: bool = False,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        data_loaders: Optional[List[DataLoader]] = None,
    ) -> List[SkillTestOutput]:
        """
        Run calibration set on an existing evaluator.
        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(self.client)
        skill_test_request = SkillTestInputRequest(
            name=name,
            test_dataset_id=test_dataset_id,
            test_data=test_data,
            prompt=prompt,
            models=[model],
            is_evaluator=True,
            pii_filter=pii_filter,
            objective=ObjectiveRequest(intent="Calibration"),
            reference_variables=_to_reference_variables(reference_variables),
            input_variables=_to_input_variables(input_variables),
            data_loaders=_to_data_loaders(data_loaders),
        )
        return api_instance.skills_calibrate_create(skill_test_request)

    def calibrate_batch(
        self,
        *,
        evaluator_definitions: List[CalibrateBatchParameters],
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        parallel_requests: int = 1,
    ) -> CalibrateBatchResult:
        """
        Run calibration for a set of prompts and models

        Args:

             evaluator_definitions: List of evaluator definitions.

             test_dataset_id: ID of the dataset to be used to test the skill.

             test_data: Actual data to be used to test the skill.

             parallel_requests: Number of parallel requests. Uses ThreadPoolExecutor if > 1.

        Returns a dictionary with the results and errors for each model and prompt.
        """

        model_errors: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"sum_squared_errors": 0, "abs_errors": 0, "count": 0}
        )
        prompt_errors: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"sum_squared_errors": 0, "abs_errors": 0, "count": 0}
        )

        all_results = []

        use_thread_pool = parallel_requests > 1

        def process_results(results: List[SkillTestOutput], param: CalibrateBatchParameters) -> None:
            for result in results:
                score = result.result["score"]
                expected_score = result.result["expected_score"]
                squared_error = (score - expected_score) ** 2
                abs_error = abs(score - expected_score)

                model_errors[param.model]["sum_squared_errors"] += squared_error
                model_errors[param.model]["abs_errors"] += abs_error
                model_errors[param.model]["count"] += 1

                prompt_errors[param.prompt]["sum_squared_errors"] += squared_error
                prompt_errors[param.prompt]["abs_errors"] += abs_error
                prompt_errors[param.prompt]["count"] += 1

                all_results.append(result)

        if use_thread_pool:
            with ThreadPoolExecutor(max_workers=parallel_requests) as executor:
                futures = {
                    executor.submit(
                        self.calibrate,
                        name=param.name,
                        test_dataset_id=test_dataset_id,
                        test_data=test_data,
                        prompt=param.prompt,
                        model=param.model,
                        pii_filter=param.pii_filter,
                        reference_variables=param.reference_variables,
                        input_variables=param.input_variables,
                        data_loaders=param.data_loaders,
                    ): param
                    for param in evaluator_definitions
                }

                for future in as_completed(futures):
                    param = futures[future]
                    try:
                        results = future.result()
                        process_results(results, param)
                    except Exception as exc:
                        raise ValueError(f"Calibration failed for {param.prompt} with model {param.model}") from exc
        else:
            for param in evaluator_definitions:
                try:
                    results = self.calibrate(
                        name=param.name,
                        test_dataset_id=test_dataset_id,
                        test_data=test_data,
                        prompt=param.prompt,
                        model=param.model,
                        pii_filter=param.pii_filter,
                        reference_variables=param.reference_variables,
                        input_variables=param.input_variables,
                        data_loaders=param.data_loaders,
                    )
                    process_results(results, param)
                except Exception as exc:
                    raise ValueError(f"Calibration failed for {param.prompt} with model {param.model}") from exc

        rms_errors_model = {
            model: math.sqrt(data["sum_squared_errors"] / data["count"])
            for model, data in model_errors.items()
            if data["count"] > 0
        }

        rms_errors_prompt = {
            prompt: math.sqrt(data["sum_squared_errors"] / data["count"])
            for prompt, data in prompt_errors.items()
            if data["count"] > 0
        }

        mae_errors_model = {
            model: data["abs_errors"] / data["count"] for model, data in model_errors.items() if data["count"] > 0
        }

        mae_errors_prompt = {
            prompt: data["abs_errors"] / data["count"] for prompt, data in prompt_errors.items() if data["count"] > 0
        }

        return CalibrateBatchResult(
            results=all_results,
            rms_errors_model=rms_errors_model,
            rms_errors_prompt=rms_errors_prompt,
            mae_errors_model=mae_errors_model,
            mae_errors_prompt=mae_errors_prompt,
        )
