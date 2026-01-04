import pytest
from pydantic import ValidationError

from openbb_tushare.models.balance_sheet import TushareBalanceSheetQueryParams
from openbb_tushare.models.cash_flow import TushareCashFlowStatementQueryParams
from openbb_tushare.models.equity_historical import TushareEquityHistoricalQueryParams
from openbb_tushare.models.equity_profile import TushareEquityProfileQueryParams
from openbb_tushare.models.equity_quote import TushareEquityQuoteQueryParams
from openbb_tushare.models.historical_dividends import TushareHistoricalDividendsQueryParams
from openbb_tushare.models.income_statement import TushareIncomeStatementQueryParams


@pytest.mark.parametrize(
    "model_cls",
    [
        TushareEquityQuoteQueryParams,
        TushareEquityProfileQueryParams,
        TushareEquityHistoricalQueryParams,
        TushareBalanceSheetQueryParams,
        TushareCashFlowStatementQueryParams,
        TushareIncomeStatementQueryParams,
        TushareHistoricalDividendsQueryParams,
    ],
)
def test_tushare_rejects_unsupported_us_symbols(model_cls):
    with pytest.raises(ValidationError) as exc:
        model_cls(symbol="AAPL")

    assert "Invalid 'symbol' market for Tushare" in str(exc.value)


def test_tushare_normalizes_yahoo_cn_symbols_to_ts_code_list():
    q = TushareEquityQuoteQueryParams(symbol="600036.SS, 000001.SZ, 430047.BJ")
    assert q.symbol == "600036.SH,000001.SZ,430047.BJ"


def test_tushare_normalizes_single_cn_symbol_across_models():
    assert TushareBalanceSheetQueryParams(symbol="600036.SS").symbol == "600036.SH"
    assert TushareCashFlowStatementQueryParams(symbol="600036.SS").symbol == "600036.SH"
    assert TushareIncomeStatementQueryParams(symbol="600036.SS").symbol == "600036.SH"
    assert TushareEquityProfileQueryParams(symbol="600036.SS").symbol == "600036.SH"


def test_tushare_historical_dividends_validates_iso_dates_when_strings():
    q = TushareHistoricalDividendsQueryParams(
        symbol="600036.SS",
        start_date="2024-01-01",
        end_date="2024-02-01",
    )
    assert q.symbol == "600036.SH"

    with pytest.raises(ValidationError) as exc:
        TushareHistoricalDividendsQueryParams(
            symbol="600036.SS",
            start_date="2024/01/01",
            end_date="2024-02-01",
        )

    assert "Invalid 'start_date' format. Expected YYYY-MM-DD." in str(exc.value)


def test_tushare_equity_historical_validates_iso_dates_when_strings():
    q = TushareEquityHistoricalQueryParams(
        symbol="600036.SS",
        start_date="2024-01-01",
        end_date="2024-02-01",
    )
    assert q.symbol == "600036.SH"

    with pytest.raises(ValidationError) as exc:
        TushareEquityHistoricalQueryParams(
            symbol="600036.SS",
            start_date="20240101",
            end_date="2024-02-01",
        )

    assert "Invalid 'start_date' format. Expected YYYY-MM-DD." in str(exc.value)
