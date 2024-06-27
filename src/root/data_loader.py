from abc import ABC
from typing import Dict, Literal, Optional, Union

from root.generated.openapi_client.models.data_loader_type_enum import DataLoaderTypeEnum as _DataLoaderTypeEnum

_EngineType = Literal["google", "bing"]
_ParameterDict = Dict[str, Union[str, Dict[str, str], None]]


class _DataLoaderBase(ABC):
    type: _DataLoaderTypeEnum
    name: str

    def _get_parameter_dict(self) -> _ParameterDict:
        raise NotImplementedError


class WebPageDataLoader(_DataLoaderBase):
    """Data loader which retrieves data from a web page

    Args:
      name: A name assigned to the data loader. The data loader name must be included in the Skill prompt variables.
      url: The URL to retrieve the data from

        Example:

          `"http://example.com/something"`
    """

    type = _DataLoaderTypeEnum.WEBPAGE

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def _get_parameter_dict(self) -> _ParameterDict:
        return {"url": self.url}


class WebSearchDataLoader(_DataLoaderBase):
    """Data loader which retrieves data from web search

    Args:
      name: A name assigned to the data loader. The data loader name must be included in the Skill prompt variables.
      engine: Search engine to use - `"google"` and `"bing"` are supported.
      search_terms: What to search for in the search engine

    """

    type = _DataLoaderTypeEnum.WEBSEARCH

    def __init__(self, name: str, engine: _EngineType, search_terms: str):
        self.name = name
        self.engine = self.validate_engine(engine)
        self.search_terms = search_terms

    def validate_engine(self, engine: str) -> str:
        """Validate that the given search engine is valid.
        ValueError is raised if it is not."""
        if engine not in ["google", "bing"]:
            raise ValueError("Engine must be 'google' or 'bing'")
        return engine

    def _get_parameter_dict(self) -> _ParameterDict:
        return {"engine": self.engine, "search_terms": self.search_terms}


class SqlDataLoader(_DataLoaderBase):
    """Data loader which retrieves data from SQL

    Args:

      name: A name assigned to the data loader. The data loader name must be included in the Skill prompt variables.

      connection_string: Connection string to use - currently it supports
        only PostgreSQL

        Example:

          `"host='localhost' dbname='my_database' user='postgres' password='secret'"`

      query: The SQL query to feed to SQL.

        Example:

          `"SELECT name FROM users"`
    """

    type = _DataLoaderTypeEnum.SQL

    def __init__(self, name: str, connection_string: str, query: str):
        self.name = name
        self.query = query
        self.connection_string = connection_string

    def _get_parameter_dict(self) -> _ParameterDict:
        return {"connection_string": self.connection_string, "query": self.query}


class ApiCallDataLoader(_DataLoaderBase):
    """Data loader which retrieves data from an URL

    Args:

      name: A name assigned to the data loader. The data loader name must be included in the Skill prompt variables.

      endpoint: URL to connect to. Request type is implicitly GET. Example: `"http://example.com/something"`

      headers: Optional set of headers to specify for the request: Example: `{"X-Accept": "application/json"}`
    """

    type = _DataLoaderTypeEnum.API_CALL

    def __init__(self, name: str, endpoint: str, headers: Optional[Dict[str, str]]):
        self.name = name
        self.endpoint = endpoint
        self.headers = headers

    def _get_parameter_dict(self) -> _ParameterDict:
        return {"endpoint": self.endpoint, "headers": self.headers}


DataLoader = Union[WebPageDataLoader, WebSearchDataLoader, SqlDataLoader, ApiCallDataLoader]
