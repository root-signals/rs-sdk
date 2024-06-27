from typing import Dict, Optional, cast

from root.generated.openapi_client.api.chats_api import ChatsApi
from root.generated.openapi_client.models.chat_detail import ChatDetail
from root.generated.openapi_client.models.chat_execution_request_request import ChatExecutionRequestRequest
from root.generated.openapi_client.models.chat_execution_result import ChatExecutionResult

from .generated.openapi_client import ApiClient


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
        self, variables: Optional[Dict[str, str]] = None, *, skill_version_id: Optional[str] = None
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
            skill_id=self.skill_id,
        )
        return api_instance.chats_execute_create(
            chat_id=self.chat_id, chat_execution_request_request=chat_execution_request
        )
