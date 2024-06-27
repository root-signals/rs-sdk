from functools import partial
from typing import Any, Dict, Iterator, Optional

import requests

from root.generated.openapi_client.api.datasets_api import DatasetsApi
from root.generated.openapi_client.models.data_set_create import DataSetCreate
from root.generated.openapi_client.models.data_set_list import DataSetList

from .generated.openapi_client import ApiClient
from .utils import iterate_cursor_list


class DataSets:
    """DataSets (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: ApiClient, base_url: str, api_key: str):
        self.client = client
        self.base_url = base_url
        self.api_key = api_key

    def create(
        self, *, name: Optional[str] = None, path: Optional[str] = None, type: str = "reference"
    ) -> Optional[DataSetCreate]:
        """
        Create a dataset object with the given parameters to the registry.
        If the dataset has a path, it will be uploaded to the registry.

        """

        payload: Dict[str, Any] = {"name": name, "type": type, "tags": []}
        if path:
            files = {"file": open(path, "rb")}

        # TODO Should use the generated client if the generator some day supports streaming upload
        # (Currently the underlying implementation loads file contents to memory always)
        response = requests.post(
            f"{self.base_url}/datasets/",
            headers={"Authorization": f"Api-Key {self.api_key}"},
            data=payload,
            files=files,
            timeout=120,
        )
        if not response.ok:
            raise Exception(f"create failed with status code {response.status_code} and message\n{response.text}")

        return DataSetCreate.from_dict(response.json())

    def get(self, dataset_id: str) -> DataSetList:
        """
        Get a dataset object from the registry.
        """
        api_instance = DatasetsApi(self.client)
        return api_instance.datasets_retrieve(dataset_id)

    def list(self, search_term: Optional[str] = None, *, limit: int = 100) -> Iterator[DataSetList]:
        """Iterate through the datasets.

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned datasets.

        """
        api_instance = DatasetsApi(self.client)
        yield from iterate_cursor_list(partial(api_instance.datasets_list, search=search_term), limit=limit)

    def delete(self, dataset_id: str) -> None:
        """
        Delete a dataset object from the registry.
        """
        api_instance = DatasetsApi(self.client)
        return api_instance.datasets_destroy(dataset_id)
