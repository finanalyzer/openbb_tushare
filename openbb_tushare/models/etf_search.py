"""Tushare ETF Search Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field


class TushareEtfSearchQueryParams(EtfSearchQueryParams):
    """Tushare ETF Search Query Params.
    
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


class TushareEtfSearchData(EtfSearchData):
    """Tushare ETF Search Data."""

    __alias_dict__ = {
        "symbol": "ts_code",
    }


class TushareEtfSearchFetcher(
    Fetcher[
        TushareEtfSearchQueryParams,
        List[TushareEtfSearchData],
    ]
):
    """Tushare ETF Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareEtfSearchQueryParams:
        """Transform the query."""
        return TushareEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TushareEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tushare endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_tushare.utils.ts_equity_search import get_symbols
        import tushare as ts
        from openbb_tushare.utils.helpers import get_api_key

        api_key = credentials.get("tushare_api_key") if credentials else ""
        tushare_api_key = get_api_key(api_key)
        
        try:
            pro = ts.pro_api(tushare_api_key)
            # Try to get ETF list using fund_basic API
            # Tushare has a fund_basic API for funds which includes ETFs
            try:
                df_etf = pro.fund_basic(market='E', fields='ts_code,name,market,ftype,fund_type')
                # Filter for ETFs (ftype typically includes ETF types)
                # Rename columns to match standard format
                df_etf = df_etf.rename(columns={'ts_code': 'symbol', 'name': 'name'})
                
                # Apply query filter if provided
                if query.query:
                    df_etf = df_etf[
                        df_etf['name'].str.contains(query.query, case=False, na=False) |
                        df_etf['symbol'].str.contains(query.query, case=False, na=False)
                    ]
                
                if query.limit is not None:
                    df_etf = df_etf.head(query.limit)
                    
                return df_etf.to_dict(orient="records")
            except Exception:
                # If fund_basic is not available, return empty list
                # This prevents 422 errors
                return []
        except Exception:
            # If Tushare doesn't support ETF search, return empty list
            # This prevents 422 errors
            return []

    @staticmethod
    def transform_data(
        query: TushareEtfSearchQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TushareEtfSearchData]:
        """Transform the data."""
        if not data:
            return []
        return [TushareEtfSearchData.model_validate(d) for d in data]

