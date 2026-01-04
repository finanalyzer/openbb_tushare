"""Tushare Historical Dividends Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)

from openbb_tushare.utils.tools import normalize_tushare_symbol_list, validate_iso_yyyy_mm_dd

import logging
from openbb_tushare.utils.tools import setup_logger
setup_logger()
logger = logging.getLogger(__name__)

class TushareHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """Tushare Historical Dividends Query."""
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

    @field_validator("start_date", "end_date", mode="before", check_fields=False)
    @classmethod
    def _validate_input_dates(cls, v: object, info):  # pylint: disable=unused-argument
        field_name = getattr(info, "field_name", "date")
        return validate_iso_yyyy_mm_dd(v, field_name)


class TushareHistoricalDividendsData(HistoricalDividendsData):
    """Tushare Historical Dividends Data. All data is split-adjusted."""
    
    @field_validator(
        "ex_dividend_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Validate dates."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None

    
class TushareHistoricalDividendsFetcher(
    Fetcher[
        TushareHistoricalDividendsQueryParams, List[TushareHistoricalDividendsData]
    ]
):
    """Tushare Historical Dividends Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any],
    ) -> TushareHistoricalDividendsQueryParams:
        """Transform the query."""
        return TushareHistoricalDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TushareHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Tushare."""
        # pylint: disable=import-outside-toplevel
        from openbb_tushare.utils.ts_historical_dividends import get_dividends
        api_key = credentials.get("tushare_api_key") if credentials else ""

        logger.info(f"Historical Dividends Fetcher start_date:{query.start_date}, end_date:{query.end_date}...")
        return get_dividends(query.symbol, query.start_date, query.end_date, query.use_cache, api_key).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TushareHistoricalDividendsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TushareHistoricalDividendsData]:
        """Transform the data."""
        #return [TushareHistoricalDividendsData.model_validate(d) for d in data]
        result: List[TushareHistoricalDividendsData] = []
        for d in data:
            result.append(TushareHistoricalDividendsData(**d))
        logger.info(
            "Transformed historical dividends completed.\n"
        )        
        return result
