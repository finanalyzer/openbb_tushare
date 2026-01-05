"""Tushare Income Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_tushare.utils.tools import normalize_tushare_symbol_list


class TushareIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Tushare Income Statement Query.

    Source: https://tushare.pro/document/2?doc_id=33
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


class TushareIncomeStatementData(IncomeStatementData):
    """Tushare Income Statement Data."""

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class TushareIncomeStatementFetcher(
    Fetcher[
        TushareIncomeStatementQueryParams,
        List[TushareIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Tushare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TushareIncomeStatementQueryParams:
        """Transform the query params."""
        return TushareIncomeStatementQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: TushareIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tushare endpoint."""
        from openbb_tushare.utils.ts_income_statement import get_income_statement
        api_key = credentials.get("tushare_api_key") if credentials else ""

        income_statement = get_income_statement(query.symbol, query.period, query.limit, query.use_cache, api_key=api_key)

        return income_statement.to_dict(orient="records")
    @staticmethod
    def transform_data(
        query: TushareIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TushareIncomeStatementData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [TushareIncomeStatementData.model_validate(d) for d in data]