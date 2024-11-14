from typing import Awaitable, Dict, Optional, cast

from .generated.openapi_aclient import ApiClient as AApiClient
from .generated.openapi_aclient.api.chats_api import ChatsApi as AChatsApi
from .generated.openapi_aclient.models.chat_detail import ChatDetail as AChatDetail
from .generated.openapi_aclient.models.chat_execution_request_request import (
    ChatExecutionRequestRequest as AChatExecutionRequestRequest,
)
from .generated.openapi_aclient.models.chat_execution_result import ChatExecutionResult as AChatExecutionResult
from .generated.openapi_client import ApiClient
from .generated.openapi_client.api.chats_api import ChatsApi
from .generated.openapi_client.models.chat_detail import ChatDetail
from .generated.openapi_client.models.chat_execution_request_request import (
    ChatExecutionRequestRequest,
)
from .generated.openapi_client.models.chat_execution_result import ChatExecutionResult


class ASkillChat(AChatDetail):
    """Wrapper for a single Chat with a Skill.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: Awaitable[AApiClient]

    @classmethod
    async def _awrap(cls, chat: AChatDetail, client: Awaitable[AApiClient]) -> "ASkillChat":
        if not isinstance(chat, AChatDetail):
            raise ValueError(f"Wrong instance in _wrap: {chat!r}")
        schat = cast(ASkillChat, chat)
        schat.__class__ = cls
        schat._client = client
        return schat

    async def arun(
        self,
        variables: Optional[Dict[str, str]] = None,
        *,
        skill_version_id: Optional[str] = None,
        _request_timeout: Optional[int] = None,
    ) -> AChatExecutionResult:
        """
        Asynchronously run a skill with optional variables as an interactive chat.
        The chat message history is stored and can be referred to in following calls.

        The response is equal to the skill run response, with the addition of a chat_id key.
        """

        api_instance = AChatsApi(await self._client())  # type: ignore[operator]
        chat_execution_request = AChatExecutionRequestRequest(
            variables=variables,
            skill_version_id=skill_version_id,
        )
        return await api_instance.chats_execute_create(
            chat_id=self.chat_id,
            chat_execution_request_request=chat_execution_request,
            _request_timeout=_request_timeout,
        )


class SkillChat(ChatDetail):
    """Wrapper for a single Chat with a Skill.

    For available attributes, please check the (automatically
    generated) superclass documentation.
    """

    _client: ApiClient

    @classmethod
    def _wrap(cls, chat: ChatDetail, client: ApiClient) -> "SkillChat":
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
        Run a skill with optional variables as an interactive chat. The chat message history is stored and can
        be referred to in following calls.

        The response is equal to the skill run response, with the addition of a chat_id key.
        """

        api_instance = ChatsApi(self._client)
        chat_execution_request = ChatExecutionRequestRequest(
            variables=variables,
            skill_version_id=skill_version_id,
        )
        return api_instance.chats_execute_create(
            chat_id=self.chat_id,
            chat_execution_request_request=chat_execution_request,
            _request_timeout=_request_timeout,
        )
