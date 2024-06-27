from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Iterator, List, Optional

from root.generated.openapi_client.api.objectives_api import ObjectivesApi
from root.generated.openapi_client.models.objective_list import ObjectiveList
from root.generated.openapi_client.models.objective_request import ObjectiveRequest

from .generated.openapi_client import ApiClient
from .skills import Skills
from .utils import iterate_cursor_list

if TYPE_CHECKING:
    from .validators import Validator


class Objectives:
    """Objectives (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient):
        self.client = client

    def create(self, *, intent: Optional[str] = None, validators: Optional[List[Validator]] = None) -> str:
        """Create a new objective and return its ID.

        Args:

          intent: The intent of the objective.

          validators: An optional list of validators.

        """
        skills = Skills(self.client)
        request = ObjectiveRequest(
            intent=intent,
            validators=[validator._to_request(skills) for validator in validators or []],
        )
        api_instance = ObjectivesApi(self.client)
        return api_instance.objectives_create(objective_request=request).id

    def delete(self, objective_id: str) -> None:
        """
        Delete the objective from the registry.

        Args:

          objective_id: The objective to be deleted.

        """
        api_instance = ObjectivesApi(self.client)
        return api_instance.objectives_destroy(id=objective_id)

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
