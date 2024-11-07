import asyncio
from typing import Awaitable, Dict, Optional, cast

from root.generated.openapi_aclient.api.chats_api import ChatsApi
from root.generated.openapi_aclient.models.chat_detail import ChatDetail
from root.generated.openapi_aclient.models.chat_execution_request_request import ChatExecutionRequestRequest
from root.generated.openapi_aclient.models.chat_execution_result import ChatExecutionResult

from .generated.openapi_aclient import ApiClient


class SkillChat(ChatDetail):
    """Wrapper for a single Chat with a Skill.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[ApiClient]

    @classmethod
    def _wrap(cls, chat: ChatDetail, client: Awaitable[ApiClient]) -> "SkillChat":
        return asyncio.run_coroutine_threadsafe(cls._awrap(chat, client), asyncio.get_event_loop()).result()

    @classmethod
    async def _awrap(cls, chat: ChatDetail, client: Awaitable[ApiClient]) -> "SkillChat":
        if not isinstance(chat, ChatDetail):
            raise ValueError(f"Wrong instance in _wrap: {chat!r}")
        schat = cast(SkillChat, chat)
        schat.__class__ = cls
        schat._client = client
        return schat

    def run(
        self,
        variables: Optional[Dict[str, str]] = None,
        *,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> ChatExecutionResult:
        """
        Synchronously run a skill with optional variables as an interactive chat.
        The chat message history is stored and can be referred to in following calls.

        The response is equal to the skill run response, with the addition of a chat_id key.
        """
        return asyncio.run_coroutine_threadsafe(
            self.arun(
                variables=variables,
                skill_version_id=skill_version_id,
                _request_timeout=_request_timeout,
            ),
            asyncio.get_event_loop(),
        ).result()

    async def arun(
        self,
        variables: Optional[Dict[str, str]] = None,
        *,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> ChatExecutionResult:
        """
        Asynchronously run a skill with optional variables as an interactive chat.
        The chat message history is stored and can be referred to in following calls.

        The response is equal to the skill run response, with the addition of a chat_id key.
        """
        api_instance = ChatsApi(await self._client())  # type: ignore[operator]
        chat_execution_request = ChatExecutionRequestRequest(
            variables=variables,
            skill_version_id=skill_version_id,
        )
        return await api_instance.chats_execute_create(
            chat_id=self.chat_id,
            chat_execution_request_request=chat_execution_request,
            _request_timeout=_request_timeout,
        )
