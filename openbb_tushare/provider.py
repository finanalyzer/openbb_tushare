"""openbb_tushare OpenBB Platform Provider."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tushare.models.available_indices import TushareAvailableIndicesFetcher
from openbb_tushare.models.equity_search import TushareEquitySearchFetcher

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
        "EquitySearch": TushareEquitySearchFetcher,
    }
)
