"""Tushare Equity Profile Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from datetime import date as dateType

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, ValidationInfo, field_validator
import pandas as pd

from openbb_tushare.utils.tools import normalize_tushare_symbol_list


class TushareEquityProfileQueryParams(EquityInfoQueryParams):
    """Tushare Equity Profile Query."""

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

class TushareEquityProfileData(EquityInfoData):
    """Tushare Equity Profile Data."""

    __alias_dict__ = {
        "symbol": "ts_code",
        "stock_exchange": "exchange",
        "long_description": "introduction",
        "ceo": "chairman",
        "company_url": "website",
        "hq_address1": "office",
        "hq_address_city": "city",
        "hq_state": "province",
        "entity_status": "list_status",
        "industry_category": "market",
    }

    @field_validator("employees", mode="before", check_fields=False)
    @classmethod
    def validate_employees(cls, v: Optional[int]) -> Optional[int]:
        """Return 0 if it is nan."""
        if v is None or v == "" or pd.isna(v):
            return 0
        else:
            return int(v)


class TushareEquityProfileFetcher(
    Fetcher[TushareEquityProfileQueryParams, List[TushareEquityProfileData]]
):
    """Tushare Equity Profile fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareEquityProfileQueryParams:
        """Transform the query."""
        return TushareEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TushareEquityProfileQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Tushare."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from warnings import warn

        api_key = credentials.get("tushare_api_key") if credentials else ""

        symbols = query.symbol.split(",")
        results = []
        messages: list = []

        async def get_one(symbol, api_key: str, use_cache: bool = True) -> None:
            from openbb_tushare.utils.ts_equity_profile import get_equity_profile
            """Get the data for one ticker symbol."""
            try:
                result: dict = {}
                result = get_equity_profile(symbol, api_key=api_key, use_cache=use_cache).to_dict(orient="records")[0]
                if result:
                    results.append(result)
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )

        tasks = [get_one(symbol, api_key=api_key, use_cache=query.use_cache) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if not results and not messages:
            raise EmptyDataError("No data was returned for any symbol")

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: TushareEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TushareEquityProfileData]:
        """Transform the data."""
        return [TushareEquityProfileData.model_validate(d) for d in data]
