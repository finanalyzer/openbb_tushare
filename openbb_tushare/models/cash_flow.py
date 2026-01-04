"""Tushare Cash Flow Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_tushare.utils.tools import normalize_tushare_symbol_list


class TushareCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Tushare Cash Flow Statement Query.

    Source: https://tushare.pro/document/2?doc_id=44
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


class TushareCashFlowStatementData(CashFlowStatementData):
    """Tushare Cash Flow Statement Data."""

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class TushareCashFlowStatementFetcher(
    Fetcher[
        TushareCashFlowStatementQueryParams,
        list[TushareCashFlowStatementData],
    ]
):
    """Tushare Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TushareCashFlowStatementQueryParams:
        """Transform the query parameters."""
        return TushareCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TushareCashFlowStatementQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the Tushare endpoints."""
        # pylint: disable=import-outside-toplevel
        from openbb_tushare.utils.ts_cash_flow import get_cash_flow
        api_key = credentials.get("tushare_api_key") if credentials else ""

        cash_flow = get_cash_flow(query.symbol, query.period, query.limit, query.use_cache, api_key=api_key)

        return cash_flow.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: TushareCashFlowStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TushareCashFlowStatementData]:
        """Transform the data."""
        return [TushareCashFlowStatementData.model_validate(d) for d in data]