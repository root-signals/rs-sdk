from functools import partial
from typing import Iterator

from root.generated.openapi_client.api.models_api import ModelsApi
from root.generated.openapi_client.models.model import Model

from .generated.openapi_client import ApiClient
from .utils import iterate_cursor_list


class Models:
    """Models (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient):
        self.client = client

    def list(self, *, limit: int = 100) -> Iterator[Model]:
        """Iterate through the models.

        Note:

          The call will list only publicly available global models and
          those models available to the organzation(s) of the user.

        Args:
          limit: Number of entries to iterate through at most.

        """
        api_instance = ModelsApi(self.client)
        yield from iterate_cursor_list(partial(api_instance.models_list), limit=limit)
