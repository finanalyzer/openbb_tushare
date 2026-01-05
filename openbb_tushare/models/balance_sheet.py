"""Tushare Balance Sheet Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_tushare.utils.tools import normalize_tushare_symbol_list


class TushareBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Tushare Balance Sheet Query.

    Source: https://tushare.pro/document/2?doc_id=36
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
        le=5,
    )
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


class TushareBalanceSheetData(BalanceSheetData):
    """Tushare Balance Sheet Data."""

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class TushareBalanceSheetFetcher(
    Fetcher[
        TushareBalanceSheetQueryParams,
        list[TushareBalanceSheetData],
    ]
):
    """Tushare Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TushareBalanceSheetQueryParams:
        """Transform the query parameters."""
        return TushareBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TushareBalanceSheetQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the Tushare endpoints."""
        # pylint: disable=import-outside-toplevel
        from openbb_tushare.utils.ts_balance_sheet import get_balance_sheet
        api_key = credentials.get("tushare_api_key") if credentials else ""

        balance_sheet = get_balance_sheet(query.symbol, query.period, query.limit, query.use_cache, api_key=api_key)

        return balance_sheet.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TushareBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TushareBalanceSheetData]:
        """Transform the data."""
        return [TushareBalanceSheetData.model_validate(d) for d in data]

