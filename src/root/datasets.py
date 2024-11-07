import asyncio
from functools import partial
from typing import AsyncIterator, Awaitable, Iterator, Optional

import aiohttp
from pydantic import StrictStr

from root.generated.openapi_aclient.api.datasets_api import DatasetsApi
from root.generated.openapi_aclient.models.data_set_create import DataSetCreate
from root.generated.openapi_aclient.models.data_set_list import DataSetList
from root.generated.openapi_aclient.models.paginated_data_set_list_list import PaginatedDataSetListList

from .generated.openapi_aclient import ApiClient
from .utils import wrap_async_iter


class DataSets:
    """DataSets (sub) API

    Note:

      The construction of the API instance should be handled by
      accesing an attribute of a :class:`root.client.RootSignals` instance.
    """

    def __init__(self, client: Awaitable[ApiClient], base_url: str, api_key: str):
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
        Synchronously create a dataset object with the given parameters to the registry.
        If the dataset has a path, it will be uploaded to the registry.

        """

        return asyncio.run_coroutine_threadsafe(
            self.acreate(name=name, path=path, type=type, _request_timeout=_request_timeout), asyncio.get_event_loop()
        ).result()

    async def acreate(
        self,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        type: str = "reference",
        _request_timeout: Optional[int] = None,
    ) -> Optional[DataSetCreate]:
        """
        Asynchronously create a dataset object with the given parameters to the registry.
        If the dataset has a path, it will be uploaded to the registry.

        """

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
                return DataSetCreate.from_dict(await response.json())

    def get(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> DataSetList:
        """
        Synchronously get a dataset object from the registry.
        """

        return asyncio.run_coroutine_threadsafe(
            self.aget(dataset_id, _request_timeout=_request_timeout), asyncio.get_event_loop()
        ).result()

    async def aget(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> DataSetList:
        """
        Asynchronously get a dataset object from the registry.
        """
        api_instance = DatasetsApi(await self.client())  # type: ignore[operator]
        return await api_instance.datasets_retrieve(dataset_id, _request_timeout=_request_timeout)

    def list(
        self, search_term: Optional[str] = None, *, limit: int = 100, _request_timeout: Optional[int] = None
    ) -> Iterator[DataSetList]:
        """Synchronously iterate through the datasets.

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned datasets.

        """
        yield from wrap_async_iter(self.alist(search_term=search_term, limit=limit, _request_timeout=_request_timeout))

    async def alist(
        self, search_term: Optional[str] = None, *, limit: int = 100, _request_timeout: Optional[int] = None
    ) -> AsyncIterator[DataSetList]:
        """Asynchronously iterate through the datasets.

        Args:
          limit: Number of entries to iterate through at most.

          search_term: Can be used to limit returned datasets.

        """

        api_instance = DatasetsApi(await self.client())  # type: ignore[operator]
        partial_list = partial(api_instance.datasets_list, search=search_term, _request_timeout=_request_timeout)

        cursor: Optional[StrictStr] = None
        while limit > 0:
            result: PaginatedDataSetListList = await partial_list(page_size=limit, cursor=cursor)
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
        Synchronously delete a dataset object from the registry.
        """
        return asyncio.run_coroutine_threadsafe(
            self.adelete(dataset_id, _request_timeout=_request_timeout), asyncio.get_event_loop()
        ).result()

    async def adelete(
        self,
        dataset_id: str,
        *,
        _request_timeout: Optional[int] = None,
    ) -> None:
        """
        Asynchronously delete a dataset object from the registry.
        """
        api_instance = DatasetsApi(await self.client())  # type: ignore[operator]
        return await api_instance.datasets_destroy(dataset_id, _request_timeout=_request_timeout)
