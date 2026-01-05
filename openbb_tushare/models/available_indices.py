"""Tushare Available Indices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from datetime import (
    date as dateType
)

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class TushareAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """Tushare Available Indices Query.

    Source: https://tushare.pro/document/2?doc_id=94
    """
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

class TushareAvailableIndicesData(AvailableIndicesData):
    """Tushare Available Indices Data."""

    __alias_dict__ = {
        "symbol": "ts_code",
    }

class TushareAvailableIndicesFetcher(
    Fetcher[
        TushareAvailableIndicesQueryParams,
        List[TushareAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the Tushare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareAvailableIndicesQueryParams:
        """Transform the query params."""
        return TushareAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TushareAvailableIndicesQueryParams,  # pylint disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        from openbb_tushare.utils.ts_available_indices import get_available_indices
        api_key = credentials.get("tushare_api_key") if credentials else ""

        return get_available_indices(query.use_cache, api_key=api_key).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TushareAvailableIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TushareAvailableIndicesData]:
        """Return the transformed data."""
        return [TushareAvailableIndicesData.model_validate(d) for d in data]
