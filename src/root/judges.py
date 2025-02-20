from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from functools import partial
from typing import AsyncIterator, Iterator, List, Optional, Union, cast

from pydantic import StrictStr

from .generated.openapi_aclient import ApiClient as AApiClient
from .generated.openapi_aclient.api.beta_api import BetaApi as ABetaApi
from .generated.openapi_aclient.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest as AEvaluatorExecutionFunctionsRequest,
)
from .generated.openapi_aclient.models.evaluator_reference_request import (
    EvaluatorReferenceRequest as AEvaluatorReferenceRequest,
)
from .generated.openapi_aclient.models.judge import Judge as AOpenApiJudge
from .generated.openapi_aclient.models.judge_execution_request import (
    JudgeExecutionRequest as AJudgeExecutionRequest,
)
from .generated.openapi_aclient.models.judge_execution_response import (
    JudgeExecutionResponse as AJudgeExecutionResponse,
)
from .generated.openapi_aclient.models.judge_list import JudgeList as AJudgeList
from .generated.openapi_aclient.models.paginated_judge_list_list import (
    PaginatedJudgeListList as APaginatedJudgeListList,
)
from .generated.openapi_aclient.models.patched_judge_request import (
    PatchedJudgeRequest as APatchedJudgeRequest,
)
from .generated.openapi_client import ApiClient
from .generated.openapi_client.api.beta_api import BetaApi
from .generated.openapi_client.models.evaluator_execution_functions_request import (
    EvaluatorExecutionFunctionsRequest,
)
from .generated.openapi_client.models.evaluator_reference_request import EvaluatorReferenceRequest
from .generated.openapi_client.models.judge import Judge as OpenApiJudge
from .generated.openapi_client.models.judge_execution_request import JudgeExecutionRequest
from .generated.openapi_client.models.judge_execution_response import JudgeExecutionResponse
from .generated.openapi_client.models.judge_list import JudgeList
from .generated.openapi_client.models.paginated_judge_list_list import PaginatedJudgeListList
from .generated.openapi_client.models.patched_judge_request import PatchedJudgeRequest
from .utils import ClientContextCallable, with_async_client, with_sync_client


class Judge(OpenApiJudge):
    """Wrapper for a single Judge.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    client_context: ClientContextCallable

    @classmethod
    def _wrap(cls, apiobj: Union[OpenApiJudge, JudgeList], client_context: ClientContextCallable) -> Judge:
        """Wrap API object into a Judge instance."""
        if not isinstance(apiobj, (OpenApiJudge, JudgeList)):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(Judge, apiobj)
        obj.__class__ = cls
        obj.client_context = client_context
        return obj

    @with_sync_client
    def run(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        _request_timeout: Optional[int] = None,
        _client: ApiClient,
    ) -> JudgeExecutionResponse:
        """
        Run the judge.

        Args:
          response: LLM output to evaluate
          request: The prompt sent to the LLM. Optional.
          contexts: Optional documents passed to RAG evaluators
          functions: Optional functions to execute
          expected_output: Optional expected output
          _request_timeout: Optional timeout for the request
        """
        api_instance = BetaApi(_client)
        execution_request = JudgeExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return api_instance.beta_judges_execute_create(
            judge_id=self.id,
            judge_execution_request=execution_request,
            _request_timeout=_request_timeout,
        )


class AJudge(AOpenApiJudge):
    """
    Async wrapper for a single Judge.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    client_context: ClientContextCallable

    @classmethod
    async def _awrap(cls, apiobj: Union[AOpenApiJudge, AJudgeList], client_context: ClientContextCallable) -> AJudge:
        if not isinstance(apiobj, (AOpenApiJudge, AJudgeList)):
            raise ValueError(f"Wrong instance in _wrap: {apiobj!r}")
        obj = cast(AJudge, apiobj)
        obj.__class__ = cls
        obj.client_context = client_context
        return obj

    @with_async_client
    async def arun(
        self,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[AEvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        _request_timeout: Optional[int] = None,
        _client: AApiClient,
    ) -> AJudgeExecutionResponse:
        """
        Asynchronously run the judge.

        Args:
          response: LLM output to evaluate
          request: The prompt sent to the LLM. Optional.
          contexts: Optional documents passed to RAG evaluators
          functions: Optional functions to execute
          expected_output: Optional expected output
          _request_timeout: Optional timeout for the request
        """
        api_instance = ABetaApi(_client)
        execution_request = AJudgeExecutionRequest(
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
            request=request,
            response=response,
        )
        return await api_instance.beta_judges_execute_create(
            judge_id=self.id,
            judge_execution_request=execution_request,
            _request_timeout=_request_timeout,
        )


class Judges:
    """
    Judges API

    Note:
        The construction of the API instance should be handled by
        accessing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client_context: ClientContextCallable):
        self.client_context = client_context

    @with_sync_client
    def get(self, judge_id: str, *, _request_timeout: Optional[int] = None, _client: ApiClient) -> Judge:
        """
        Get a judge by ID.

        Args:
          judge_id: The judge to be fetched.
        """
        api_instance = BetaApi(_client)
        return Judge._wrap(
            api_instance.beta_judges_retrieve(id=judge_id, _request_timeout=_request_timeout),
            client_context=self.client_context,
        )

    @with_async_client
    async def aget(self, judge_id: str, *, _request_timeout: Optional[int] = None, _client: AApiClient) -> AJudge:
        """
        Asynchronously get a judge by ID.

        Args:
          judge_id: The judge to be fetched.
        """
        api_instance = ABetaApi(_client)
        return await AJudge._awrap(
            await api_instance.beta_judges_retrieve(id=judge_id, _request_timeout=_request_timeout),
            client_context=self.client_context,
        )

    @with_sync_client
    def delete(self, judge_id: str, *, _request_timeout: Optional[int] = None, _client: ApiClient) -> None:
        """
        Delete the judge.

        Args:
          judge_id: The judge to be deleted.
        """
        api_instance = BetaApi(_client)
        return api_instance.beta_judges_destroy(id=judge_id, _request_timeout=_request_timeout)

    @with_async_client
    async def adelete(self, judge_id: str, *, _request_timeout: Optional[int] = None, _client: AApiClient) -> None:
        """
        Asynchronously delete the judge.

        Args:
          judge_id: The judge to be deleted.
        """
        api_instance = ABetaApi(_client)
        return await api_instance.beta_judges_destroy(id=judge_id, _request_timeout=_request_timeout)

    @with_sync_client
    def list(self, *, limit: int = 100, _client: ApiClient) -> Iterator[Judge]:
        """
        Iterate through the judges.

        Args:
          limit: Number of entries to iterate through at most.
        """
        api_instance = BetaApi(_client)
        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: PaginatedJudgeListList = api_instance.beta_judges_list(page_size=limit, cursor=cursor)
            if not result.results:
                return

            used_results = result.results[:limit]
            limit -= len(used_results)
            for judge in used_results:
                yield Judge._wrap(judge, client_context=self.client_context)

            if not (cursor := result.next):
                return

    async def alist(self, *, limit: int = 100) -> AsyncIterator[AJudge]:
        """
        Asynchronously iterate through the judges.

        Args:
          limit: Number of entries to iterate through at most.
        """
        context = self.client_context()
        assert isinstance(context, AbstractAsyncContextManager), "This method is not available in synchronous mode"
        async with context as client:
            api_instance = ABetaApi(client)
            partial_list = partial(api_instance.beta_judges_list)

            cursor: Optional[StrictStr] = None
            while limit > 0:
                result: APaginatedJudgeListList = await partial_list(page_size=limit, cursor=cursor)
                if not result.results:
                    return

                used_results = result.results[:limit]
                limit -= len(used_results)
                for judge in used_results:
                    yield await AJudge._awrap(judge, client_context=self.client_context)

                if not (cursor := result.next):
                    return

    @with_sync_client
    def update(
        self,
        judge_id: str,
        *,
        name: Optional[str] = None,
        evaluator_references: Optional[List[EvaluatorReferenceRequest]] = None,
        _request_timeout: Optional[int] = None,
        _client: ApiClient,
    ) -> Judge:
        """
        Update an existing judge.

        Args:
          judge_id: The judge to be updated.
          name: New name for the judge
          evaluator_references: New list of evaluator references
        """
        api_instance = BetaApi(_client)
        request = PatchedJudgeRequest(
            name=name,
            evaluator_references=evaluator_references,
        )
        return Judge._wrap(
            api_instance.beta_judges_partial_update(
                id=judge_id,
                patched_judge_request=request,
                _request_timeout=_request_timeout,
            ),
            client_context=self.client_context,
        )

    @with_async_client
    async def aupdate(
        self,
        judge_id: str,
        *,
        name: Optional[str] = None,
        evaluator_references: Optional[List[AEvaluatorReferenceRequest]] = None,
        _request_timeout: Optional[int] = None,
        _client: AApiClient,
    ) -> AJudge:
        """
        Asynchronously update an existing judge.

        Args:
          judge_id: The judge to be updated.
          name: New name for the judge
          evaluator_references: New list of evaluator references
        """
        api_instance = ABetaApi(_client)
        request = APatchedJudgeRequest(
            name=name,
            evaluator_references=evaluator_references,
        )
        return await AJudge._awrap(
            await api_instance.beta_judges_partial_update(
                id=judge_id,
                patched_judge_request=request,
                _request_timeout=_request_timeout,
            ),
            client_context=self.client_context,
        )

    @with_sync_client
    def run(
        self,
        judge_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[EvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        _request_timeout: Optional[int] = None,
        _client: ApiClient,
    ) -> JudgeExecutionResponse:
        """
        Run a judge directly by ID.

        Args:
          judge_id: ID of the judge to run
          response: LLM output to evaluate
          request: The prompt sent to the LLM. Optional.
          contexts: Optional documents passed to RAG evaluators
          functions: Optional functions to execute
          expected_output: Optional expected output
          _request_timeout: Optional timeout for the request
        """
        api_instance = BetaApi(_client)
        execution_request = JudgeExecutionRequest(
            request=request,
            response=response,
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
        )
        return api_instance.beta_judges_execute_create(
            judge_id=judge_id,
            judge_execution_request=execution_request,
            _request_timeout=_request_timeout,
        )

    @with_async_client
    async def arun(
        self,
        judge_id: str,
        *,
        response: str,
        request: Optional[str] = None,
        contexts: Optional[List[str]] = None,
        functions: Optional[List[AEvaluatorExecutionFunctionsRequest]] = None,
        expected_output: Optional[str] = None,
        _request_timeout: Optional[int] = None,
        _client: AApiClient,
    ) -> AJudgeExecutionResponse:
        """
        Asynchronously run a judge directly by ID.

        Args:
          judge_id: ID of the judge to run
          response: LLM output to evaluate
          request: The prompt sent to the LLM. Optional.
          contexts: Optional documents passed to RAG evaluators
          functions: Optional functions to execute
          expected_output: Optional expected output
          _request_timeout: Optional timeout for the request
        """
        api_instance = ABetaApi(_client)
        execution_request = AJudgeExecutionRequest(
            contexts=contexts,
            functions=functions,
            expected_output=expected_output,
            request=request,
            response=response,
        )
        return await api_instance.beta_judges_execute_create(
            judge_id=judge_id,
            judge_execution_request=execution_request,
            _request_timeout=_request_timeout,
        )
