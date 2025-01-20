from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel, Field

from .generated.openapi_aclient.models.data_loader_type_enum import DataLoaderTypeEnum as _ADataLoaderTypeEnum
from .generated.openapi_client.models.data_loader_type_enum import DataLoaderTypeEnum as _DataLoaderTypeEnum

EngineType = Literal["google", "bing"]


class WebPageDataLoader(BaseModel):
    """Data loader which retrieves data from a web page"""

    type: _DataLoaderTypeEnum = Field(default=_DataLoaderTypeEnum.WEBPAGE, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    url: str = Field(..., description="The URL to retrieve the data from")

    def get_parameters(self) -> Dict[str, str]:
        return {"url": self.url}


class AWebPageDataLoader(BaseModel):
    """Data loader which retrieves data from a web page"""

    type: _ADataLoaderTypeEnum = Field(default=_ADataLoaderTypeEnum.WEBPAGE, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    url: str = Field(..., description="The URL to retrieve the data from")

    def get_parameters(self) -> Dict[str, str]:
        return {"url": self.url}


class WebSearchDataLoader(BaseModel):
    """Data loader which retrieves data from web search"""

    type: _DataLoaderTypeEnum = Field(default=_DataLoaderTypeEnum.WEBSEARCH, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    engine: EngineType = Field(..., description="Search engine to use")
    search_terms: str = Field(..., description="What to search for in the search engine")

    def get_parameters(self) -> Dict[str, str]:
        return {"engine": self.engine, "search_terms": self.search_terms}


class AWebSearchDataLoader(BaseModel):
    """Data loader which retrieves data from web search"""

    type: _ADataLoaderTypeEnum = Field(default=_ADataLoaderTypeEnum.WEBSEARCH, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    engine: EngineType = Field(..., description="Search engine to use")
    search_terms: str = Field(..., description="What to search for in the search engine")

    def get_parameters(self) -> Dict[str, str]:
        return {"engine": self.engine, "search_terms": self.search_terms}


class SqlDataLoader(BaseModel):
    """Data loader which retrieves data from SQL"""

    type: _DataLoaderTypeEnum = Field(default=_DataLoaderTypeEnum.SQL, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    connection_string: str = Field(..., description="PostgreSQL connection string")
    query: str = Field(..., description="SQL query to execute")

    def get_parameters(self) -> Dict[str, str]:
        return {"connection_string": self.connection_string, "query": self.query}


class ASqlDataLoader(BaseModel):
    """Data loader which retrieves data from SQL"""

    type: _ADataLoaderTypeEnum = Field(default=_ADataLoaderTypeEnum.SQL, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    connection_string: str = Field(..., description="PostgreSQL connection string")
    query: str = Field(..., description="SQL query to execute")

    def get_parameters(self) -> Dict[str, str]:
        return {"connection_string": self.connection_string, "query": self.query}


class ApiCallDataLoader(BaseModel):
    """Data loader which retrieves data from an URL"""

    type: _DataLoaderTypeEnum = Field(default=_DataLoaderTypeEnum.API_CALL, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    endpoint: str = Field(..., description="URL to connect to (GET request)")
    headers: Optional[Dict[str, str]] = Field(None, description="Optional request headers")

    def get_parameters(self) -> Dict[str, Union[str, Dict[str, str], None]]:
        return {"endpoint": self.endpoint, "headers": self.headers}


class AApiCallDataLoader(BaseModel):
    """Data loader which retrieves data from an URL"""

    type: _ADataLoaderTypeEnum = Field(default=_ADataLoaderTypeEnum.API_CALL, frozen=True)
    name: str = Field(..., description="Name assigned to the data loader")
    endpoint: str = Field(..., description="URL to connect to (GET request)")
    headers: Optional[Dict[str, str]] = Field(None, description="Optional request headers")

    def get_parameters(self) -> Dict[str, Union[str, Dict[str, str], None]]:
        return {"endpoint": self.endpoint, "headers": self.headers}


DataLoader = Union[WebPageDataLoader, WebSearchDataLoader, SqlDataLoader, ApiCallDataLoader]
ADataLoader = Union[AWebPageDataLoader, AWebSearchDataLoader, ASqlDataLoader, AApiCallDataLoader]
