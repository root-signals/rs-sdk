from functools import partial
from typing import Any, AsyncIterator, Awaitable, Dict, Iterator, Optional, Union

import aiohttp
import requests
from pydantic import StrictStr

from .generated.openapi_aclient import ApiClient as AApiClient
from .generated.openapi_aclient.api.datasets_api import DatasetsApi as ADatasetsApi
from .generated.openapi_aclient.models.data_set_create import DataSetCreate as ADataSetCreate
from .generated.openapi_aclient.models.data_set_list import DataSetList as ADataSetList
from .generated.openapi_aclient.models.paginated_data_set_list_list import (
    PaginatedDataSetListList as APaginatedDataSetListList,
)
from .generated.openapi_client import ApiClient
from .generated.openapi_client.api.datasets_api import DatasetsApi
from .generated.openapi_client.models.data_set_create import DataSetCreate
from .generated.openapi_client.models.data_set_list import DataSetList
from .utils import iterate_cursor_list


class DataSets:
    """DataSets (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: Union[Awaitable[AApiClient], ApiClient], base_url: str, api_key: str):
        self.client = client
        self.base_url = base_url
        self.api_key = api_key

    def create(
        self,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        type: str = "reference",
        _request_timeout: Optional[int] = None,
    ) -> Optional[DataSetCreate]:
        """
        Create a dataset object with the given parameters to the registry.
        If the dataset has a path, it will be uploaded to the registry.

        """

        if not isinstance(self.client, ApiClient) and self.client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

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
            timeout=_request_timeout or 120,
        )
        if not response.ok:
            raise Exception(f"create failed with status code {response.status_code} and message\n{response.text}")

        return DataSetCreate.from_dict(response.json())

    async def acreate(
        self,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        type: str = "reference",
        _request_timeout: Optional[int] = None,
    ) -> Optional[ADataSetCreate]:
        """
        Asynchronously create a dataset object with the given parameters to the registry.
        If the dataset has a path, it will be uploaded to the registry.

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        payload = aiohttp.FormData()
        payload.add_field("name", name)
        payload.add_field("type", type)

        if path:
            file = open(path, "rb")
            payload.add_field("file", file)

        # TODO Should use the generated client if the generator some day supports streaming upload
        # (Currently the underlying implementation loads file contents to memory always)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/datasets/",
                data=payload,
                headers={"Authorization": f"Api-Key {self.api_key}"},
                timeout=aiohttp.ClientTimeout(_request_timeout) or aiohttp.ClientTimeout(120),
            ) as response:
                if not response.ok:
                    raise Exception(f"create failed with status code {response.status} and message\n{response.text}")
                if not file.closed:
                    file.close()
                return ADataSetCreate.from_dict(await response.json())

    def get(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> DataSetList:
        """
        Get a dataset object from the registry.
        """

        if not isinstance(self.client, ApiClient) and self.client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = DatasetsApi(self.client)
        return api_instance.datasets_retrieve(dataset_id, _request_timeout=_request_timeout)

    async def aget(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> ADataSetList:
        """
        Asynchronously get a dataset object from the registry.
        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = ADatasetsApi(await self.client())  # type: ignore[operator]
        return await api_instance.datasets_retrieve(dataset_id, _request_timeout=_request_timeout)

    def list(
        self, search_term: Optional[str] = None, *, limit: int = 100, _request_timeout: Optional[int] = None
    ) -> Iterator[DataSetList]:
        """Iterate through the datasets.

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned datasets.

        """
        if not isinstance(self.client, ApiClient) and self.client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = DatasetsApi(self.client)
        yield from iterate_cursor_list(
            partial(api_instance.datasets_list, search=search_term, _request_timeout=_request_timeout), limit=limit
        )

    async def alist(
        self, search_term: Optional[str] = None, *, limit: int = 100, _request_timeout: Optional[int] = None
    ) -> AsyncIterator[ADataSetList]:
        """Asynchronously iterate through the datasets.

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned datasets.

        """

        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        api_instance = ADatasetsApi(await self.client())  # type: ignore[operator]
        partial_list = partial(api_instance.datasets_list, search=search_term, _request_timeout=_request_timeout)

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: APaginatedDataSetListList = await partial_list(page_size=limit, cursor=cursor)
            if not result.results:
                return

            used_results = result.results[:limit]
            for used_result in used_results:
                yield used_result

                limit -= len(used_results)
                if not (cursor := result.next):
                    return

    def delete(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> None:
        """
        Delete a dataset object from the registry.
        """

        if not isinstance(self.client, ApiClient) and self.client.__name__ == "_aapi_client":  # type: ignore[attr-defined]
            raise Exception("This method is not available in asynchronous mode")

        api_instance = DatasetsApi(self.client)
        return api_instance.datasets_destroy(dataset_id, _request_timeout=_request_timeout)

    async def adelete(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> None:
        if isinstance(self.client, ApiClient):
            raise Exception("This method is not available in synchronous mode")

        """
        Asynchronously delete a dataset object from the registry.
        """
        api_instance = ADatasetsApi(await self.client())  # type: ignore[operator]
        return await api_instance.datasets_destroy(dataset_id, _request_timeout=_request_timeout)
