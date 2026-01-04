"""Tushare Equity Quote Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field, field_validator
import logging
from openbb_tushare.utils.tools import setup_logger, normalize_tushare_symbol_list

setup_logger()
logger = logging.getLogger(__name__)

class TushareEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Tushare Equity Quote Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _normalize_symbol(cls, v: object) -> object:
        if v is None:
            return v
        return normalize_tushare_symbol_list(str(v))


class TushareEquityQuoteData(EquityQuoteData):
    """Tushare Equity Quote Data."""

    __alias_dict__ = {
        "symbol": "ts_code",
    }


class TushareEquityQuoteFetcher(
    Fetcher[TushareEquityQuoteQueryParams, List[TushareEquityQuoteData]]
):
    """Tushare Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareEquityQuoteQueryParams:
        """Transform the query."""
        return TushareEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TushareEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Tushare."""
        # pylint: disable=import-outside-toplevel
        from openbb_tushare.utils.ts_equity_quote import get_one
        import pandas as pd

        api_key = credentials.get("tushare_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        all_data = []

        for symbol in symbols:
            try:        
                data = get_one(symbol, query.use_cache, api_key=api_key)
                if data is None or data.empty:
                    logger.warning(f"No data returned for symbol {symbol}")
                    continue
                records = data.to_dict(orient="records")
                if records:
                    all_data.append(records[0])
                else:
                    logger.warning(f"Empty records for symbol {symbol}")
                
            except Exception as e:
                logger.error(f"Error fetching data for symbol {symbol}: {e}")
                continue

        return all_data

    @staticmethod
    def transform_data(
        query: TushareEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TushareEquityQuoteData]:
        """Transform the data."""
        return [TushareEquityQuoteData.model_validate(d) for d in data]
