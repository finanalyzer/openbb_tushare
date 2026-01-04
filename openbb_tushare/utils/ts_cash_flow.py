import logging
import pandas as pd
import tushare as ts
from typing import Optional, Literal
from openbb_tushare.utils.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key
from openbb_tushare.utils.tools import normalize_symbol

setup_logger()
logger = logging.getLogger(__name__)

def get_cash_flow(
        symbol: str, 
        period: Literal["annual", "quarter"] = "annual",
        limit: Optional[int] = 5,
        use_cache: bool = True,
        api_key : Optional[str] = ""
    ) -> pd.DataFrame:
    from openbb_tushare.utils.blob_cache import BlobCache
    cache = BlobCache(table_name="cash_flow")
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
        cash_flow_df = pro.hk_cashflow(ts_code=normalized_ts_code)
    else:
        cash_flow_df = pro.cashflow(ts_code=normalized_ts_code)
        cash_flow_df = cash_flow_df.drop_duplicates(subset='end_date', keep='first')
    
    return cash_flow_df

def processing_data(cash_flow_df: pd.DataFrame) -> pd.DataFrame:
    from openbb_tushare.utils.helpers import get_fiscal_period
    # logger.info("Processing cash flow data")
    selected_columns = cash_flow_df[['n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act']]
    selected_columns = selected_columns.rename(columns={'n_cashflow_act':'net_cash_from_operating_activities', 
                                                        'n_cashflow_inv_act':'net_cash_from_investing_activities',
                                                        'n_cash_flows_fnc_act':'net_cash_from_financing_activities'})

    # Extract year from end_date and create fiscal_year column
    selected_columns.loc[:, 'fiscal_year'] = pd.to_datetime(cash_flow_df['end_date']).dt.year
    selected_columns.loc[:, 'period_ending'] = pd.to_datetime(cash_flow_df['end_date'])
    selected_columns.loc[:, 'fiscal_period'] = cash_flow_df['end_type'].apply(get_fiscal_period)
    return selected_columns