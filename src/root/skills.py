from __future__ import annotations

import asyncio
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Dict, Iterator, List, Literal, Optional, Union, cast

from pydantic import BaseModel, StrictStr

from root.generated.openapi_aclient.api.chats_api import ChatsApi
from root.generated.openapi_aclient.api.objectives_api import ObjectivesApi
from root.generated.openapi_aclient.api.skills_api import SkillsApi
from root.generated.openapi_aclient.models.chat_create_request import ChatCreateRequest
from root.generated.openapi_aclient.models.data_loader_request import DataLoaderRequest
from root.generated.openapi_aclient.models.evaluator_calibration_output import EvaluatorCalibrationOutput
from root.generated.openapi_aclient.models.input_variable_request import InputVariableRequest
from root.generated.openapi_aclient.models.objective_request import ObjectiveRequest
from root.generated.openapi_aclient.models.paginated_skill_list import PaginatedSkillList
from root.generated.openapi_aclient.models.paginated_skill_list_output_list import PaginatedSkillListOutputList
from root.generated.openapi_aclient.models.patched_skill_request import PatchedSkillRequest
from root.generated.openapi_aclient.models.reference_variable_request import ReferenceVariableRequest
from root.generated.openapi_aclient.models.skill import Skill as OpenAPISkill
from root.generated.openapi_aclient.models.skill_execution_request import SkillExecutionRequest
from root.generated.openapi_aclient.models.skill_execution_result import SkillExecutionResult
from root.generated.openapi_aclient.models.skill_list_output import SkillListOutput
from root.generated.openapi_aclient.models.skill_request import SkillRequest
from root.generated.openapi_aclient.models.skill_test_data_request import SkillTestDataRequest
from root.generated.openapi_aclient.models.skill_test_input_request import SkillTestInputRequest
from root.generated.openapi_aclient.models.skill_test_output import SkillTestOutput
from root.generated.openapi_aclient.models.skill_validator_execution_request import (
    SkillValidatorExecutionRequest,
)
from root.generated.openapi_aclient.models.validator_execution_result import (
    ValidatorExecutionResult,
)
from root.utils import wrap_async_iter

from .data_loader import DataLoader
from .generated.openapi_aclient import ApiClient
from .generated.openapi_aclient.models import (
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
    results: List[EvaluatorCalibrationOutput]
    rms_errors_model: Dict[str, float]
    mae_errors_model: Dict[str, float]
    rms_errors_prompt: Dict[str, float]
    mae_errors_prompt: Dict[str, float]


class Versions:
    """Version listing (sub)API

    Note that this should not be directly instantiated.
    """

    def __init__(self, client: Awaitable[ApiClient]):
        self._client = client

    def list(self, skill_id: str) -> PaginatedSkillList:
        """Synchronously list all versions of a skill.

        Args:
          skill_id: The skill to list the versions for
        """
        return asyncio.run_coroutine_threadsafe(self.alist(skill_id), asyncio.get_event_loop()).result()

    async def alist(self, skill_id: str) -> PaginatedSkillList:
        """Asynchronously list all versions of a skill.

        Args:
          skill_id: The skill to list the versions for
        """
        api_instance = SkillsApi(await self._client())  # type: ignore[operator]
        return await api_instance.get_a_list_of_all_versions_of_a_skill(id=skill_id)


class Skill(OpenAPISkill):
    """Wrapper for a single Skill.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[ApiClient]

    @classmethod
    def _wrap(cls, apiobj: OpenAPISkill, client: Awaitable[ApiClient]) -> "Skill":
        return asyncio.run_coroutine_threadsafe(cls._awrap(apiobj, client), asyncio.get_event_loop()).result()

    @classmethod
    async def _awrap(cls, apiobj: OpenAPISkill, client: Awaitable[ApiClient]) -> "Skill":
        if not isinstance(apiobj, OpenAPISkill):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(Skill, apiobj)
        obj.__class__ = cls
        obj._client = client
        return obj

    @property
    def openai_base_url(self) -> str:
        """
        Synchronously get the OpenAI compatibility API URL for the skill.

        Currently only OpenAI chat completions API is supported using
        the base URL.
        """
        return asyncio.run_coroutine_threadsafe(self.aopenai_base_url(), asyncio.get_event_loop()).result()

    async def aopenai_base_url(self) -> str:
        """
        Asynchronously get the OpenAI compatibility API URL for the skill.

        Currently only OpenAI chat completions API is supported using
        the base URL.
        """
        client = await self._client()  # type: ignore[operator]
        return f"{client.configuration._base_path}/skills/openai/{self.id}"

    def run(self, variables: Optional[Dict[str, str]] = None) -> SkillExecutionResult:
        """Synchronously run a skill with optional variables.

        Args:
          variables: The variables to be provided to the skill.
        """
        return asyncio.run_coroutine_threadsafe(self.arun(variables), asyncio.get_event_loop()).result()

    async def arun(self, variables: Optional[Dict[str, str]] = None) -> SkillExecutionResult:
        """Asynchronously run a skill with optional variables.

        Args:
          variables: The variables to be provided to the skill.
        """

        api_instance = SkillsApi(await self._client())  # type: ignore[operator]
        skill_execution_request = SkillExecutionRequest(
            variables=variables,
            skill_version_id=self.version_id,
        )
        return await api_instance.skills_execute_create(id=self.id, skill_execution_request=skill_execution_request)

    def evaluate(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Synchronously run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """
        return asyncio.run_coroutine_threadsafe(
            self.aevaluate(
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def aevaluate(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Asynchronously run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

        """
        api_instance = SkillsApi(await self._client())  # type: ignore[operator]
        skill_execution_request = SkillValidatorExecutionRequest(
            skill_version_id=None,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return await api_instance.skills_execute_validators_create(
            id=self.id,
            skill_validator_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )


class Evaluator(OpenAPISkill):
    """Wrapper for a single Evaluator.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[ApiClient]

    @classmethod
    def _wrap(cls, apiobj: OpenAPISkill, client: Awaitable[ApiClient]) -> "Evaluator":
        return asyncio.run_coroutine_threadsafe(cls._awrap(apiobj, client), asyncio.get_event_loop()).result()

    @classmethod
    async def _awrap(cls, apiobj: OpenAPISkill, client: Awaitable[ApiClient]) -> "Evaluator":
        if not isinstance(apiobj, OpenAPISkill):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(Evaluator, apiobj)
        obj.__class__ = cls
        obj._client = client
        return obj

    def run(
        self,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
    ) -> EvaluatorExecutionResult:
        """
        Synchronously run the evaluator.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          functions: Optional list of evaluator execution functions.

          expected_output: Optional expected output for the evaluator.

        """
        return asyncio.run_coroutine_threadsafe(
            self.arun(
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                expected_output=expected_output,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def arun(
        self,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
    ) -> EvaluatorExecutionResult:
        """
        Asynchronously run the evaluator.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          functions: Optional list of evaluator execution functions.

          expected_output: Optional expected output for the evaluator.

        """

        api_instance = SkillsApi(await self._client())  # type: ignore[operator]

        evaluator_execution_request = EvaluatorExecutionRequest(
            skill_version_id=self.version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return await api_instance.skills_evaluator_execute_create(
            skill_id=self.id,
            evaluator_execution_request=evaluator_execution_request,
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


class PresetEvaluatorRunner:
    _client: Awaitable[ApiClient]

    def __init__(self, client: Awaitable[ApiClient], skill_id: str, skill_version_id: Optional[str] = None):
        self._client = client
        self.skill_id = skill_id
        self.skill_version_id = skill_version_id

    def __call__(
        self,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
    ) -> EvaluatorExecutionResult:
        """
        Synchronously run the evaluator.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          functions: Optional list of evaluator execution functions.

          expected_output: Optional expected output for the evaluator.

        """
        return asyncio.run_coroutine_threadsafe(
            self._acall(
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                expected_output=expected_output,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def _acall(
        self,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
    ) -> EvaluatorExecutionResult:
        """
        Asynchronously run the evaluator.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          functions: Optional list of evaluator execution functions.

          expected_output: Optional expected output for the evaluator.

        """

        api_instance = SkillsApi(await self._client())  # type: ignore[operator]

        evaluator_execution_request = EvaluatorExecutionRequest(
            skill_version_id=self.skill_version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return await api_instance.skills_evaluator_execute_create(
            skill_id=self.skill_id,
            evaluator_execution_request=evaluator_execution_request,
        )


class Skills:
    """Skills API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: Awaitable[ApiClient]):
        self.client = client
        self.versions = Versions(client)

    async def _to_objective_request(
        self, *, intent: Optional[str] = None, validators: Optional[List[Validator]] = None
    ) -> ObjectiveRequest:
        return ObjectiveRequest(
            intent=intent,
            validators=[await validator._to_request(self) for validator in validators or []],
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
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Synchronously create a new skill and return the result

        Args:

          prompt: The prompt that is provided to the model (not used
          if using OpenAI compatibility API)

          name: Name of the skill (defaulting to <unnamed>)

          objective_id: Already created objective id to assign to the skill.

          intent: The intent of the skill (defaulting to name); not available if objective_id is set.

          model: The model to use (defaults to 'root', which means
            Root Signals default at the time of skill creation)

          fallback_models: The fallback models to use in case the primary model fails.

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
        return asyncio.run_coroutine_threadsafe(
            self.acreate(
                prompt=prompt,
                name=name,
                intent=intent,
                model=model,
                system_message=system_message,
                fallback_models=fallback_models,
                pii_filter=pii_filter,
                validators=validators,
                reference_variables=reference_variables,
                input_variables=input_variables,
                is_evaluator=is_evaluator,
                data_loaders=data_loaders,
                model_params=model_params,
                objective_id=objective_id,
                overwrite=overwrite,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def acreate(
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
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Asynchronously create a new skill and return the result

        Args:

          prompt: The prompt that is provided to the model (not used
          if using OpenAI compatibility API)

          name: Name of the skill (defaulting to <unnamed>)

          objective_id: Already created objective id to assign to the skill.

          intent: The intent of the skill (defaulting to name); not available if objective_id is set.

          model: The model to use (defaults to 'root', which means
            Root Signals default at the time of skill creation)

          fallback_models: The fallback models to use in case the primary model fails.

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

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        objective: Optional[ObjectiveRequest] = None
        if objective_id is None:
            if intent is None:
                intent = name
            objective = await self._to_objective_request(intent=intent, validators=validators)
            objectives_api_instance = ObjectivesApi(await self.client())  # type: ignore[operator]
            new_objective = await objectives_api_instance.objectives_create(objective_request=objective)
            objective_id = new_objective.id
        else:
            if intent:
                raise ValueError("Supplying both objective_id and intent is not supported")
            if validators:
                raise ValueError("Supplying both objective_id and validators is not supported")

        skill_request = SkillRequest(
            name=name,
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

        skill = await api_instance.skills_create(skill_request=skill_request, _request_timeout=_request_timeout)
        return await Skill._awrap(skill, self.client)

    def update(
        self,
        skill_id: str,
        *,
        change_note: Optional[str] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        fallback_models: Optional[List[ModelName]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        model: Optional[ModelName] = None,
        name: Optional[str] = None,
        pii_filter: Optional[bool] = None,
        prompt: Optional[str] = None,
        is_evaluator: Optional[bool] = None,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        evaluator_demonstrations: Optional[List[EvaluatorDemonstration]] = None,
        objective_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Synchronously update existing skill instance and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        Args:
          skill_id: The skill to be updated
        """
        return asyncio.run_coroutine_threadsafe(
            self.aupdate(
                skill_id,
                change_note=change_note,
                data_loaders=data_loaders,
                fallback_models=fallback_models,
                input_variables=input_variables,
                model=model,
                name=name,
                pii_filter=pii_filter,
                prompt=prompt,
                is_evaluator=is_evaluator,
                reference_variables=reference_variables,
                model_params=model_params,
                evaluator_demonstrations=evaluator_demonstrations,
                objective_id=objective_id,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def aupdate(
        self,
        skill_id: str,
        *,
        change_note: Optional[str] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        fallback_models: Optional[List[ModelName]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        model: Optional[ModelName] = None,
        name: Optional[str] = None,
        pii_filter: Optional[bool] = None,
        prompt: Optional[str] = None,
        is_evaluator: Optional[bool] = None,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        evaluator_demonstrations: Optional[List[EvaluatorDemonstration]] = None,
        objective_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Asynchronously update existing skill instance and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        Args:
          skill_id: The skill to be updated
        """

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        request = PatchedSkillRequest(
            name=name,
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
            objective_id=objective_id,
        )
        api_response = await api_instance.skills_partial_update(
            id=skill_id, patched_skill_request=request, _request_timeout=_request_timeout
        )
        return await Skill._awrap(api_response, self.client)

    def get(
        self,
        skill_id: str,
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Synchronously get a Skill instance by ID.

        Args:
          skill_id: The skill to be fetched
        """
        return asyncio.run_coroutine_threadsafe(
            self.aget(skill_id, _request_timeout=_request_timeout), asyncio.get_event_loop()
        ).result()

    async def aget(
        self,
        skill_id: str,
        _request_timeout: Optional[int] = None,
    ) -> Skill:
        """Asynchronously get a Skill instance by ID.

        Args:
          skill_id: The skill to be fetched
        """
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        api_response = await api_instance.skills_retrieve(id=skill_id, _request_timeout=_request_timeout)
        return await Skill._awrap(api_response, self.client)

    def list(
        self,
        search_term: Optional[str] = None,
        *,
        limit: int = 100,
        name: Optional[str] = None,
        only_evaluators: bool = False,
    ) -> Iterator[SkillListOutput]:
        """Synchronously iterate through the skills.

        Note that call will list only publicly available global skills, and
        those models within organization that are available to the current
        user (or all if the user is an admin).

        Args:
          limit: Number of entries to iterate through at most.

          name: Specific name the returned skills must match.

          only_evaluators: Match only Skills with is_evaluator=True.

          search_term: Can be used to limit returned skills.
        """
        yield from wrap_async_iter(
            self.alist(
                search_term=search_term,
                limit=limit,
                name=name,
                only_evaluators=only_evaluators,
            )
        )

    async def alist(
        self,
        search_term: Optional[str] = None,
        *,
        limit: int = 100,
        name: Optional[str] = None,
        only_evaluators: bool = False,
    ) -> AsyncIterator[SkillListOutput]:
        """Asynchronously iterate through the skills.

        Note that call will list only publicly available global skills, and
        those models within organization that are available to the current
        user (or all if the user is an admin).

        Args:
          limit: Number of entries to iterate through at most.

          name: Specific name the returned skills must match.

          only_evaluators: Match only Skills with is_evaluator=True.

          search_term: Can be used to limit returned skills.
        """

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        partial_list = partial(
            api_instance.skills_list, name=name, search=search_term, is_evaluator=True if only_evaluators else None
        )

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: PaginatedSkillListOutputList = await partial_list(page_size=limit, cursor=cursor)
            if not result.results:
                return

            used_results = result.results[:limit]
            for used_result in used_results:
                yield used_result

                limit -= len(used_results)
                if not (cursor := result.next):
                    return

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
        _request_timeout: Optional[int] = None,
    ) -> List[SkillTestOutput]:
        """
        Synchronously test a skill definition with a test dataset and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        """
        return asyncio.run_coroutine_threadsafe(
            self.atest(
                test_dataset_id=test_dataset_id,
                prompt=prompt,
                model=model,
                fallback_models=fallback_models,
                pii_filter=pii_filter,
                validators=validators,
                reference_variables=reference_variables,
                input_variables=input_variables,
                data_loaders=data_loaders,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def atest(
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
        _request_timeout: Optional[int] = None,
    ) -> List[SkillTestOutput]:
        """
        Asynchronously test a skill definition with a test dataset and return the result.

        For description of the rest of the arguments, please refer to create
        method.

        """
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        skill_test_request = SkillTestInputRequest(
            test_dataset_id=test_dataset_id,
            prompt=prompt,
            models=[model] + (fallback_models or []),
            pii_filter=pii_filter,
            objective=await self._to_objective_request(validators=validators),
            reference_variables=_to_reference_variables(reference_variables),
            input_variables=_to_input_variables(input_variables),
            data_loaders=_to_data_loaders(data_loaders),
        )
        return await api_instance.skills_test_create(skill_test_request, _request_timeout=_request_timeout)

    def test_existing(
        self,
        skill_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        _request_timeout: Optional[int] = None,
    ) -> List[SkillTestOutput]:
        """
        Synchronously test an existing skill.

        Note that only one of the test_data and test_data_set must be provided.

        Args:

          test_data: Actual data to be used to test the skill.

          test_dataset_id: ID of the dataset to be used to test the skill.

        """
        return asyncio.run_coroutine_threadsafe(
            self.atest_existing(
                skill_id=skill_id,
                test_dataset_id=test_dataset_id,
                test_data=test_data,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def atest_existing(
        self,
        skill_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        _request_timeout: Optional[int] = None,
    ) -> List[SkillTestOutput]:
        """
        Asynchronously test an existing skill.

        Note that only one of the test_data and test_data_set must be provided.

        Args:

          test_data: Actual data to be used to test the skill.

          test_dataset_id: ID of the dataset to be used to test the skill.

        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        skill_test_request = SkillTestDataRequest(
            test_dataset_id=test_dataset_id,
            test_data=test_data,
        )
        return await api_instance.skills_test_create2(skill_id, skill_test_request, _request_timeout=_request_timeout)

    def create_chat(
        self,
        skill_id: str,
        *,
        chat_id: Optional[str] = None,
        name: Optional[str] = None,
        history_from_chat_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> SkillChat:
        """
        Synchronously create and store chat object with the given parameters.

        Args:

          skill_id: The skill to chat with.

          chat_id: Optional identifier to identify the chat. If not supplied, one is automatically generated.

          name: Optional name for the chat.

          history_from_chat_id: Optional chat_id to copy chat history from.
        """
        return asyncio.run_coroutine_threadsafe(
            self.acreate_chat(skill_id, chat_id=chat_id, name=name, history_from_chat_id=history_from_chat_id),
            asyncio.get_event_loop(),
        ).result()

    async def acreate_chat(
        self,
        skill_id: str,
        *,
        chat_id: Optional[str] = None,
        name: Optional[str] = None,
        history_from_chat_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> SkillChat:
        """
        Asynchronously create and store chat object with the given parameters.

        Args:

          skill_id: The skill to chat with.

          chat_id: Optional identifier to identify the chat. If not supplied, one is automatically generated.

          name: Optional name for the chat.

          history_from_chat_id: Optional chat_id to copy chat history from.
        """
        api_instance = ChatsApi(await self.client())  # type: ignore[operator]
        chat_create_request = ChatCreateRequest(
            name=name,
            skill_id=skill_id,
            chat_id=chat_id,
            history_from_chat_id=history_from_chat_id,
        )
        if chat_id:
            return await SkillChat._awrap(
                await api_instance.chats_initiate_create2(chat_id=chat_id, chat_create_request=chat_create_request),
                self.client,
            )
        else:
            return await SkillChat._awrap(
                await api_instance.chats_initiate_create(chat_create_request, _request_timeout=_request_timeout),
                self.client,
            )

    def delete(self, skill_id: str) -> None:
        """
        Synchronously delete the skill from the registry.

        Args:

          skill_id: The skill to be deleted.

        """
        return asyncio.run_coroutine_threadsafe(self.adelete(skill_id), asyncio.get_event_loop()).result()

    async def adelete(self, skill_id: str) -> None:
        """
        Asynchronously delete the skill from the registry.

        Args:

          skill_id: The skill to be deleted.

        """
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        return await api_instance.skills_destroy(id=skill_id)

    def run(
        self,
        skill_id: str,
        variables: Optional[Dict[str, str]] = None,
        *,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> SkillExecutionResult:
        """
        Synchronously run a skill with optional variables, model parameters, and a skill version id.
        If no skill version id is given, the latest version of the skill will be used.
        If model parameters are not given, Skill model params will be used. If the skill has no model params
        the default model parameters will be used.

        Returns a dictionary with the following keys:
        - llm_output: the LLM response of the skill run
        - validation: the result of the skill validation
        """
        return asyncio.run_coroutine_threadsafe(
            self.arun(
                skill_id,
                variables,
                model_params=model_params,
                skill_version_id=skill_version_id,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def arun(
        self,
        skill_id: str,
        variables: Optional[Dict[str, str]] = None,
        *,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> SkillExecutionResult:
        """
        Asynchronously run a skill with optional variables, model parameters, and a skill version id.
        If no skill version id is given, the latest version of the skill will be used.
        If model parameters are not given, Skill model params will be used. If the skill has no model params
        the default model parameters will be used.

        Returns a dictionary with the following keys:
        - llm_output: the LLM response of the skill run
        - validation: the result of the skill validation
        """

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        skill_execution_request = SkillExecutionRequest(
            variables=variables,
            skill_version_id=skill_version_id,
            model_params=_to_model_params(model_params),
        )

        return await api_instance.skills_execute_create(
            id=skill_id,
            skill_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )

    def evaluate(
        self,
        skill_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Synchronously run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          skill_version_id: Skill version id. If omitted, the latest version is used.

        """

        return asyncio.run_coroutine_threadsafe(
            self.aevaluate(
                skill_id,
                response=response,
                request=request,
                contexts=contexts,
                functions=functions,
                skill_version_id=skill_version_id,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def aevaluate(
        self,
        skill_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> ValidatorExecutionResult:
        """
        Asynchronously run all validators attached to a skill.

        Args:

          response: LLM output.

          request: The prompt sent to the LLM. Optional.

          contexts: Optional documents passed to RAG evaluators

          skill_version_id: Skill version id. If omitted, the latest version is used.

        """

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        skill_execution_request = SkillValidatorExecutionRequest(
            skill_version_id=skill_version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
        )
        return await api_instance.skills_execute_validators_create(
            id=skill_id,
            skill_validator_execution_request=skill_execution_request,
            _request_timeout=_request_timeout,
        )


class Evaluators:
    """Evaluators (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    # Accessed via https://api.app.rootsignals.ai/v1/skills/?page_size=60&is_evaluator=true&ordering=-created_at&status=public
    class Eval(Enum):
        # TODO: These eval names should be retrieved automatically from the API or a shared config file
        Faithfulness = "901794f9-634c-4852-9e41-7c558f1ff1ab"
        Relevance = "bd789257-f458-4e9e-8ce9-fa6e86dc3fb9"
        Clarity = "9976d9f3-7265-4732-b518-d61c2642b14e"
        Non_toxicity = "e296e374-7539-4eb2-a74a-47847dd26fb8"
        Helpfulness = "88bc92d5-bebf-45e4-9cd1-dfa33309c320"
        Politeness = "2856903a-e48c-4548-b3fe-520fd88c4f25"
        Formality = "8ab6cf1a-42b5-4a23-a15c-21372816483d"
        Harmlessness = "379fee0a-4fd1-4942-833b-7d78d78b334d"
        Confidentiality = "2eaa0a02-47a9-48f7-9b47-66ad257f93eb"
        Persuasiveness = "85bb6a74-f5dd-4130-8dcc-cffdf72327cc"
        JSON_Empty_Values_Ratio = "03829088-1799-438e-ae30-1db60832e52d"
        JSON_Property_Name_Accuracy = "740923aa-8ffd-49cc-a95d-14f831243b25"
        JSON_Property_Type_Accuracy = "eabc6924-1fec-4e96-82ce-c03bf415c885"
        JSON_Property_Completeness = "e5de37f7-d20c-420f-8072-f41dce96ecfc"
        JSON_Content_Accuracy = "b6a9aeff-c888-46d7-9e9c-7cf8cb461762"
        Context_Recall = "8bb60975-5062-4367-9fc6-a920044cba56"
        Answer_Correctness = "d4487568-4243-4da8-9c76-adbaf762dbe0"
        Answer_Semantic_Similarity = "ff350bce-4b07-4af7-9640-803c9d3c2ff9"
        Sentiment_recognition = "e3782c1e-eaf4-4b2d-8d26-53db2160f1fd"
        Safety_for_Children = "39a8b5ba-de77-4726-a6b0-621d40b3cdf5"
        Precision = "767bdd49-5f8c-48ca-8324-dfd6be7f8a79"
        Originality = "e72cb54f-548a-44f9-a6ca-4e14e5ade7f7"
        Engagingness = "64729487-d4a8-42d8-bd9e-72fd8390c134"
        Conciseness = "be828d33-158a-4e92-a2eb-f4d96c13f956"
        Coherence = "e599886c-c338-458f-91b3-5d7eba452618"
        Quality_of_Writing_Professional = "059affa9-2d1c-48de-8e97-f81dd3fc3cbe"
        Quality_of_Writing_Creative = "060abfb6-57c9-43b5-9a6d-8a1a9bb853b8"
        Truthfulness = "053df10f-b0c7-400b-892e-46ce3aa1e430"
        Context_Precision = "9d1e9a25-7e76-4771-b1e3-40825d7918c5"
        Answer_Relevance = "0907d422-e94f-4c9c-a63d-ec0eefd8a903"

    def __init__(self, client: Awaitable[ApiClient]):
        self.client = client
        self.versions = Versions(client)

    EvaluatorName = Literal[
        "Faithfulness",
        "Relevance",
        "Clarity",
        "Non_toxicity",
        "Helpfulness",
        "Politeness",
        "Formality",
        "Harmlessness",
        "Confidentiality",
        "Persuasiveness",
        "JSON_Empty_Values_Ratio",
        "JSON_Property_Name_Accuracy",
        "JSON_Property_Type_Accuracy",
        "JSON_Property_Completeness",
        "JSON_Content_Accuracy",
        "Context_Recall",
        "Answer_Correctness",
        "Answer_Semantic_Similarity",
        "Sentiment_recognition",
        "Safety_for_Children",
        "Precision",
        "Originality",
        "Engagingness",
        "Conciseness",
        "Coherence",
        "Quality_of_Writing_Professional",
        "Quality_of_Writing_Creative",
        "Truthfulness",
        "Context_Precision",
        "Answer_Relevance",
    ]

    def __getattr__(self, name: Union[EvaluatorName, str]) -> "PresetEvaluatorRunner":
        if name in self.Eval.__members__:
            return PresetEvaluatorRunner(self.client, self.Eval.__members__[name].value)
        raise AttributeError(f"{name} is not a valid attribute")

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
        _request_timeout: Optional[int] = None,
    ) -> EvaluatorExecutionResult:
        """
        Synchronously run an evaluator using its id and an optional version id .
        If no evaluator version id is given, the latest version of the evaluator will be used.

        Returns a dictionary with the following keys:
        - score: a value between 0 and 1 representing the score of the evaluator
        """
        return asyncio.run_coroutine_threadsafe(
            self.arun(
                evaluator_id,
                request=request,
                response=response,
                contexts=contexts,
                functions=functions,
                expected_output=expected_output,
                evaluator_version_id=evaluator_version_id,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def arun(
        self,
        evaluator_id: str,
        *,
        request: str,
        response: str,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        evaluator_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> EvaluatorExecutionResult:
        """
        Asynchronously run an evaluator using its id and an optional version id .
        If no evaluator version id is given, the latest version of the evaluator will be used.

        Returns a dictionary with the following keys:
        - score: a value between 0 and 1 representing the score of the evaluator
        """
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        evaluator_execution_request = EvaluatorExecutionRequest(
            skill_version_id=evaluator_version_id,
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return await api_instance.skills_evaluator_execute_create(
            skill_id=evaluator_id,
            evaluator_execution_request=evaluator_execution_request,
            _request_timeout=_request_timeout,
        )

    def calibrate_existing(
        self,
        evaluator_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        _request_timeout: Optional[int] = None,
    ) -> List[EvaluatorCalibrationOutput]:
        """
        Synchronously run calibration set on an existing evaluator.
        """
        return asyncio.run_coroutine_threadsafe(
            self.acalibrate_existing(
                evaluator_id=evaluator_id,
                test_dataset_id=test_dataset_id,
                test_data=test_data,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def acalibrate_existing(
        self,
        evaluator_id: str,
        *,
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        _request_timeout: Optional[int] = None,
    ) -> List[EvaluatorCalibrationOutput]:
        """
        Asynchronously run calibration set on an existing evaluator.
        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
        skill_test_request = SkillTestDataRequest(
            test_dataset_id=test_dataset_id,
            test_data=test_data,
        )
        return await api_instance.skills_calibrate_create2(
            evaluator_id, skill_test_request, _request_timeout=_request_timeout
        )

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
        _request_timeout: Optional[int] = None,
    ) -> List[EvaluatorCalibrationOutput]:
        """
        Synchronously run calibration set on an existing evaluator.
        """
        return asyncio.run_coroutine_threadsafe(
            self.acalibrate(
                name=name,
                test_dataset_id=test_dataset_id,
                test_data=test_data,
                prompt=prompt,
                model=model,
                pii_filter=pii_filter,
                reference_variables=reference_variables,
                input_variables=input_variables,
                data_loaders=data_loaders,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def acalibrate(
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
        _request_timeout: Optional[int] = None,
    ) -> List[EvaluatorCalibrationOutput]:
        """
        Asynchronously run calibration set on an existing evaluator.
        """
        if not test_dataset_id and not test_data:
            raise ValueError("Either test_dataset_id or test_data must be provided")
        if test_dataset_id and test_data:
            raise ValueError("Only one of test_dataset_id or test_data must be provided")
        api_instance = SkillsApi(await self.client())  # type: ignore[operator]
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
        return await api_instance.skills_calibrate_create(skill_test_request, _request_timeout=_request_timeout)

    def calibrate_batch(
        self,
        *,
        evaluator_definitions: List[CalibrateBatchParameters],
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        parallel_requests: int = 1,
        _request_timeout: Optional[int] = None,
    ) -> CalibrateBatchResult:
        """
        Synchronously run calibration for a set of prompts and models

        Args:

             evaluator_definitions: List of evaluator definitions.

             test_dataset_id: ID of the dataset to be used to test the skill.

             test_data: Actual data to be used to test the skill.

             parallel_requests: Number of parallel requests. Uses ThreadPoolExecutor if > 1.

        Returns a dictionary with the results and errors for each model and prompt.
        """
        return asyncio.run_coroutine_threadsafe(
            self.acalibrate_batch(
                evaluator_definitions=evaluator_definitions,
                test_dataset_id=test_dataset_id,
                test_data=test_data,
                parallel_requests=parallel_requests,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def acalibrate_batch(
        self,
        *,
        evaluator_definitions: List[CalibrateBatchParameters],
        test_dataset_id: Optional[str] = None,
        test_data: Optional[List[List[str]]] = None,
        parallel_requests: int = 1,
        _request_timeout: Optional[int] = None,
    ) -> CalibrateBatchResult:
        """
        Asynchronously run calibration for a set of prompts and models

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

        def process_results(results: List[EvaluatorCalibrationOutput], param: CalibrateBatchParameters) -> None:
            for result in results:
                score = result.result.score or 0
                expected_score = result.result.expected_score or 0
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
                        _request_timeout=_request_timeout,
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
                    results = await self.acalibrate(
                        name=param.name,
                        test_dataset_id=test_dataset_id,
                        test_data=test_data,
                        prompt=param.prompt,
                        model=param.model,
                        pii_filter=param.pii_filter,
                        reference_variables=param.reference_variables,
                        input_variables=param.input_variables,
                        data_loaders=param.data_loaders,
                        _request_timeout=_request_timeout,
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

    def get_by_name(self, name: str) -> Evaluator:
        """Synchronously get an evaluator instance by name.

        Args:
        name: The evaluator to be fetched. Note this only works for uniquely named evaluators.
        """

        return asyncio.run_coroutine_threadsafe(self.aget_by_name(name), asyncio.get_event_loop()).result()

    async def aget_by_name(self, name: str) -> Evaluator:
        """Asynchronously get an evaluator instance by name.

        Args:
        name: The evaluator to be fetched. Note this only works for uniquely named evaluators.
        """

        api_instance = SkillsApi(await self.client())  # type: ignore[operator]

        evaluator_list: List[SkillListOutput] = []
        async for skill in iterate_cursor_list(  # type: ignore[var-annotated]
            partial(api_instance.skills_list, name=name, is_evaluator=True),
            limit=1,
        ):
            evaluator_list.extend(skill)

        if not evaluator_list:
            raise ValueError(f"No evaluator found with name '{name}'")

        evaluator = evaluator_list[0]
        api_response = await api_instance.skills_retrieve(id=evaluator.id)

        return await Evaluator._awrap(api_response, self.client)

    def create(
        self,
        predicate: str = "",
        *,
        name: Optional[str] = None,
        intent: Optional[str] = None,
        model: Optional[ModelName] = None,
        fallback_models: Optional[List[ModelName]] = None,
        pii_filter: bool = False,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        objective_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> Evaluator:
        """Synchronously create a new evaluator and return the result
        Args:

          predicate: The question / predicate that is provided to the semantic quantification layer to
          transform it into a final prompt before being passed to the model (not used
          if using OpenAI compatibility API)

          name: Name of the skill (defaulting to <unnamed>)

          objective_id: Already created objective id to assign to the eval skill.

          intent: The intent of the skill (defaulting to name); not available if objective_id is set.

          model: The model to use (defaults to 'root', which means
            Root Signals default at the time of skill creation)
          fallback_models: The fallback models to use in case the primary model fails.

          pii_filter: Whether to use PII filter or not.

          reference_variables: An optional list of input variables for
            the skill.

          input_variables: An optional list of reference variables for
            the skill.

          data_loaders: An optional list of data loaders, which
            populate the reference variables.

          model_params: An optional set of additional parameters to the model.

          overwrite: Whether to overwrite a skill with the same name if it exists.

        """
        return asyncio.run_coroutine_threadsafe(
            self.acreate(
                predicate=predicate,
                name=name,
                intent=intent,
                model=model,
                fallback_models=fallback_models,
                pii_filter=pii_filter,
                reference_variables=reference_variables,
                input_variables=input_variables,
                data_loaders=data_loaders,
                model_params=model_params,
                objective_id=objective_id,
                overwrite=overwrite,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def acreate(
        self,
        predicate: str = "",
        *,
        name: Optional[str] = None,
        intent: Optional[str] = None,
        model: Optional[ModelName] = None,
        fallback_models: Optional[List[ModelName]] = None,
        pii_filter: bool = False,
        reference_variables: Optional[Union[List[ReferenceVariable], List[ReferenceVariableRequest]]] = None,
        input_variables: Optional[Union[List[InputVariable], List[InputVariableRequest]]] = None,
        data_loaders: Optional[List[DataLoader]] = None,
        model_params: Optional[Union[ModelParams, ModelParamsRequest]] = None,
        objective_id: Optional[str] = None,
        overwrite: bool = False,
    ) -> Evaluator:
        """Asynchronously create a new evaluator and return the result
        Args:

          predicate: The question / predicate that is provided to the semantic quantification layer to
          transform it into a final prompt before being passed to the model (not used
          if using OpenAI compatibility API)

          name: Name of the skill (defaulting to <unnamed>)

          objective_id: Already created objective id to assign to the eval skill.

          intent: The intent of the skill (defaulting to name); not available if objective_id is set.

          model: The model to use (defaults to 'root', which means
            Root Signals default at the time of skill creation)
          fallback_models: The fallback models to use in case the primary model fails.

          pii_filter: Whether to use PII filter or not.

          reference_variables: An optional list of input variables for
            the skill.

          input_variables: An optional list of reference variables for
            the skill.

          data_loaders: An optional list of data loaders, which
            populate the reference variables.

          model_params: An optional set of additional parameters to the model.

          overwrite: Whether to overwrite a skill with the same name if it exists.

        """
        _eval_skill = await Skills(self.client).acreate(
            name=name,
            prompt=predicate,
            model=model,
            intent=intent,
            system_message="",
            fallback_models=fallback_models,
            pii_filter=pii_filter,
            validators=None,
            reference_variables=reference_variables,
            input_variables=input_variables,
            is_evaluator=True,
            data_loaders=data_loaders,
            model_params=model_params,
            objective_id=objective_id,
            overwrite=overwrite,
        )
        return await Evaluator._awrap(_eval_skill, self.client)
