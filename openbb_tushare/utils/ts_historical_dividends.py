import logging
import pandas as pd
import tushare as ts
from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional, Union
from openbb_tushare.utils.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key
from openbb_tushare.utils.tools import normalize_symbol
from openbb_tushare.utils.table_cache import TableCache

setup_logger()
logger = logging.getLogger(__name__)

def get_dividends(
        symbol: str, 
        start_date: Optional[dateType] = None,
        end_date: Optional[dateType] = None,
        use_cache: bool = True,
        api_key : str = ""
    ) -> pd.DataFrame:
    """
    Get dividend history for a given symbol.
    Args:
        symbol (str): The stock symbol to query.
        start_date (dateType): The start date for the query in YYYY-MM-DD format.
        end_date (dateType): The end date for the query in YYYY-MM-DD format.
        use_cache (bool): Whether to use cached data.
        api_key (str): Tushare API key.
    """
    from openbb_tushare.utils.blob_cache import BlobCache
    cache = BlobCache(table_name="historical_dividends")
    data = cache.load_cached_data(symbol, "annual", use_cache, get_tushare_data, api_key=api_key)
    if start_date is None or end_date is None:
        return data
    else:
        return data[(data['ex_dividend_date'] >= start_date.strftime('%Y%m%d')) & (data['ex_dividend_date'] <= end_date.strftime('%Y%m%d'))].reset_index(drop=True)

def get_tushare_data(
        symbol: str,
        period: str = "annual",
        api_key : Optional[str] = ""
    ) -> pd.DataFrame:
    tushare_api_key = get_api_key(api_key)
    pro = ts.pro_api(tushare_api_key)
    _, normalized_ts_code, _ = normalize_symbol(symbol)
    div_df = pro.dividend(ts_code=normalized_ts_code)
    div_df = div_df[div_df['cash_div'] != 0].reset_index(drop=True)
    div_df = div_df.rename(columns={'cash_div':'amount', 'ex_date':'ex_dividend_date'})
    div_df['ex_dividend_date'] = pd.to_datetime(div_df['ex_dividend_date'], format='%Y%m%d')
    return div_df
