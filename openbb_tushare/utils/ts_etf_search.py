import logging

import pandas as pd
import tushare as ts
from openbb_tushare.utils.table_cache import TableCache
from openbb_tushare.utils.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key

TABLE_SCHEMA = {
    "ts_code": "TEXT PRIMARY KEY",  # Trading symbol/code (e.g. 159919.SZ)
    "symbol": "TEXT",               # Symbol (e.g. 159919)
    "name": "TEXT",                 # Short name of the ETF
    "management": "TEXT",           # Fund management company
    "custodian": "TEXT",            # Custodian bank
    "fund_type": "TEXT",            # Fund type (e.g. ETF)
    "found_date": "TEXT",           # Founding date (YYYYMMDD)
    "due_date": "TEXT",             # Due date (YYYYMMDD)
    "list_date": "TEXT",            # Listing date (YYYYMMDD)
    "issue_amount": "REAL",         # Issue amount
    "m_fee": "REAL",                # Management fee
    "c_fee": "REAL",                # Custodian fee
    "duration_year": "REAL",        # Duration in years
    "p_value": "REAL",              # Net asset value per unit
    "min_amount": "REAL",           # Minimum subscription amount
    "exp_return": "REAL",           # Expected return
    "benchmark": "TEXT",            # Benchmark index
    "status": "TEXT",               # Status (L/D/I)
    "invest_type": "TEXT",          # Investment type
    "type": "TEXT",                 # Type
    "trustee": "TEXT",              # Trustee
    "purc_startdate": "TEXT",       # Purchase start date (YYYYMMDD)
    "redm_startdate": "TEXT",       # Redemption start date (YYYYMMDD)
    "market": "TEXT",               # Market (E/O)
}

setup_logger()
logger = logging.getLogger(__name__)

def get_etf_symbols(use_cache: bool = True, api_key: str = "") -> pd.DataFrame:
    """Get ETF symbols from Tushare API.
    
    Args:
        use_cache: Whether to use cached data
        api_key: Tushare API key
        
    Returns:
        DataFrame containing ETF information
    """
    tushare_api_key = get_api_key(api_key)

    cache = TableCache(TABLE_SCHEMA, table_name="etf_symbols", primary_key="ts_code")
    if use_cache:
        data = cache.read_dataframe()
        if not data.empty:
            logger.info("Loading ETF symbols from cache...")
            return data

    logger.info("Fetching ETF symbols from Tushare API...")
    pro = ts.pro_api(tushare_api_key)
    
    # Get all funds and filter for ETFs
    # market='E' means E-market (ETF market)
    df_all = pro.fund_basic(market='E')
    
    if df_all.empty:
        logger.warning("No ETF data returned from Tushare API")
        return pd.DataFrame(columns=list(TABLE_SCHEMA.keys()))
    
    # Filter for ETF type if fund_type column exists
    if 'fund_type' in df_all.columns:
        df_etf = df_all[df_all['fund_type'] == 'ETF'].copy()
    else:
        # If fund_type doesn't exist, assume all are ETFs (since market='E')
        df_etf = df_all.copy()
    
    # Ensure required fields for EquitySearchData compatibility
    # Extract symbol from ts_code (e.g., 159919.SZ -> 159919)
    if 'ts_code' in df_etf.columns and 'symbol' not in df_etf.columns:
        df_etf['symbol'] = df_etf['ts_code'].str.replace(r'\.[A-Z]+$', '', regex=True)
    
    # Extract exchange from ts_code (e.g., 159919.SZ -> SZ)
    if 'ts_code' in df_etf.columns:
        if 'exchange' not in df_etf.columns:
            df_etf['exchange'] = df_etf['ts_code'].str.extract(r'\.([A-Z]+)$')[0]
        # Map exchange codes: SZ -> SZSE, SH -> SSE
        df_etf['exchange'] = df_etf['exchange'].replace({'SZ': 'SZSE', 'SH': 'SSE'})
    
    # Ensure name field exists (required by EquitySearchData)
    if 'name' not in df_etf.columns:
        if 'fund_name' in df_etf.columns:
            df_etf['name'] = df_etf['fund_name']
        elif 'symbol' in df_etf.columns:
            df_etf['name'] = df_etf['symbol']
        else:
            df_etf['name'] = ''
    
    # Fill missing values with empty strings for text fields, 0 for numeric fields
    text_cols = df_etf.select_dtypes(include=['object']).columns
    numeric_cols = df_etf.select_dtypes(include=['number']).columns
    df_etf[text_cols] = df_etf[text_cols].fillna('')
    df_etf[numeric_cols] = df_etf[numeric_cols].fillna(0)
    
    # Select only columns that exist in TABLE_SCHEMA
    available_cols = [col for col in TABLE_SCHEMA.keys() if col in df_etf.columns]
    df_etf = df_etf[available_cols]
    
    cache.write_dataframe(df_etf)
    logger.info(f"Fetched {len(df_etf)} ETF symbols")
    
    return df_etf

