import logging
import pandas as pd
import tushare as ts
from typing import Optional, Literal
from openbb_tushare.utils.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key
from openbb_tushare.utils.tools import normalize_symbol

setup_logger()
logger = logging.getLogger(__name__)

def get_balance_sheet(
        symbol: str, 
        period: Literal["annual", "quarter"] = "annual",
        limit: Optional[int] = 5,
        use_cache: bool = True,
        api_key : Optional[str] = ""
    ) -> pd.DataFrame:
    from openbb_tushare.utils.blob_cache import BlobCache
    cache = BlobCache(table_name="balance_sheet")
    data = cache.load_cached_data(symbol, "quarter", use_cache, get_tushare_data, api_key=api_key)
    if data is None:
        return pd.DataFrame()
    else:
        if period == "annual":
            # Filter rows where end_date ends with "1231"
            data = data[data['end_date'].astype(str).str.endswith('1231')]

        # Apply limit if specified
        if limit is not None:
            data = data.head(limit)
        
        return processing_data(data)
def get_tushare_data(
        symbol: str,
        period: str = "annual",
        api_key : Optional[str] = ""
    ) -> pd.DataFrame:
    tushare_api_key = get_api_key(api_key)
    pro = ts.pro_api(tushare_api_key)
    _, normalized_ts_code, market = normalize_symbol(symbol)
    if market == 'HK':
        balancesheet_df = pro.hk_balancesheet(ts_code=normalized_ts_code)
    else:
        balancesheet_df = pro.balancesheet(ts_code=normalized_ts_code)
        balancesheet_df = balancesheet_df.drop_duplicates(subset='end_date', keep='first')

    
    return balancesheet_df

def processing_data(balancesheet_df: pd.DataFrame) -> pd.DataFrame:
    from openbb_tushare.utils.helpers import get_fiscal_period
    # logger.info("Processing balance sheet data")
    selected_columns = balancesheet_df[['total_assets', 'total_liab']]
    selected_columns = selected_columns.rename(columns={'total_liab':'total_liabilities'})

    # Extract year from end_date and create fiscal_year column
    selected_columns.loc[:, 'fiscal_year'] = pd.to_datetime(balancesheet_df['end_date']).dt.year
    selected_columns.loc[:, 'period_ending'] = pd.to_datetime(balancesheet_df['end_date'])
    selected_columns.loc[:, 'fiscal_period'] = balancesheet_df['end_type'].apply(get_fiscal_period)
    return selected_columns