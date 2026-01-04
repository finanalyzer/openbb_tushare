"""openbb_tushare OpenBB Platform Provider."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tushare.models.available_indices import TushareAvailableIndicesFetcher
from openbb_tushare.models.balance_sheet import TushareBalanceSheetFetcher
from openbb_tushare.models.cash_flow import TushareCashFlowStatementFetcher
from openbb_tushare.models.equity_historical import TushareEquityHistoricalFetcher
from openbb_tushare.models.equity_profile import TushareEquityProfileFetcher
from openbb_tushare.models.equity_quote import TushareEquityQuoteFetcher
from openbb_tushare.models.equity_search import TushareEquitySearchFetcher
from openbb_tushare.models.etf_search import TushareEtfSearchFetcher
from openbb_tushare.models.historical_dividends import TushareHistoricalDividendsFetcher
from openbb_tushare.models.income_statement import TushareIncomeStatementFetcher

# mypy: disable-error-code="list-item"

provider = Provider(
    name="tushare",
    description="Data provider for openbb_tushare.",
    credentials=["api_key"],
    website="https://github.com/finanalyzer/openbb_tushare",
    # Here, we list out the fetchers showing what our provider can get.
    # The dictionary key is the fetcher's name, used in the `router.py`.
    fetcher_dict={
        "AvailableIndices": TushareAvailableIndicesFetcher,
        "BalanceSheet": TushareBalanceSheetFetcher,
        "CashFlowStatement": TushareCashFlowStatementFetcher,
        "EquityHistorical": TushareEquityHistoricalFetcher,
        "EquityInfo": TushareEquityProfileFetcher,
        "EquityQuote": TushareEquityQuoteFetcher,
        "EquitySearch": TushareEquitySearchFetcher,
        "EtfSearch": TushareEtfSearchFetcher,
        "HistoricalDividends": TushareHistoricalDividendsFetcher,
        "IncomeStatement": TushareIncomeStatementFetcher,
    }
)
