"""Tushare Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field
import logging
from openbb_tushare import project_name
from mysharelib.tools import setup_logger

setup_logger(project_name)
logger = logging.getLogger(__name__)


class TushareEquitySearchQueryParams(EquitySearchQueryParams):
    """Tushare Equity Search Query.

    Source: https://tushare.pro/document/2?doc_id=25
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class TushareEquitySearchData(EquitySearchData):
    """Tushare Equity Search Data."""


class TushareEquitySearchFetcher(
    Fetcher[
        TushareEquitySearchQueryParams,
        List[TushareEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the Tushare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareEquitySearchQueryParams:
        """Transform the query."""
        return TushareEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TushareEquitySearchQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tushare endpoint."""

        from openbb_tushare.utils.ts_equity_search import get_symbols
        api_key = credentials.get("tushare_api_key") if credentials else ""
        data = get_symbols(query.use_cache, api_key=api_key)
        if query.limit: data = data.head(query.limit)

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TushareEquitySearchQueryParams, data: Dict, **kwargs: Any
    ) -> List[TushareEquitySearchData]:
        """Transform the data to the standard format."""
        if query.query:
            filtered = [
                d for d in data
                if query.query in d.get('name', '') or query.query in d.get('symbol', '')
            ]
            logger.info(f"Searching for {query.query} and found {len(filtered)} results.")
            return [TushareEquitySearchData.model_validate(d) for d in filtered]

        return [TushareEquitySearchData.model_validate(d) for d in data]
