import logging

import pandas as pd
import tushare as ts
from mysharelib.table_cache import TableCache
from mysharelib.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key
from openbb_tushare import project_name

setup_logger(project_name)
logger = logging.getLogger(__name__)

TABLE_SCHEMA = {
    "ts_code": "TEXT PRIMARY KEY",  # Trading symbol/code 
    "symbol": "TEXT",               # Symbol (e.g. 600000)
    "name": "TEXT",                 # Short name of the asset
    "area": "TEXT",                 # Geographic region
    "industry": "TEXT",             # Industry classification
    "fullname": "TEXT",             # Full legal name
    "enname": "TEXT",               # English name
    "cnspell": "TEXT",              # Chinese phonetic abbreviation
    "market": "TEXT",               # Market classification (e.g. A-shares)
    "exchange": "TEXT",             # Exchange code (e.g. SSE/SZSE)
    "curr_type": "TEXT",            # Currency type (CNY/USD/HKD)
    "list_status": "TEXT",          # Listing status (L/D/P)
    "list_date": "TEXT",            # Listing date (YYYYMMDD)
    "delist_date": "TEXT",          # Delisting date (YYYYMMDD)
    "is_hs": "TEXT",                # Hong Kong Connect eligibility (N/H/S)
    "act_name": "TEXT",             # Actual controller name
    "act_ent_type": "TEXT",         # Controller entity type
    "trade_unit": "TEXT",           # Trading unit (e.g. 100 shares)
    "isin": "TEXT",                 # International Securities Identification Number
}

def get_symbols(use_cache: bool = True, api_key : str = "") -> pd.DataFrame:
    tushare_api_key = get_api_key(api_key)

    cache = TableCache(TABLE_SCHEMA, project=project_name, table_name="symbols", primary_key="ts_code")
    if use_cache:
        data = cache.read_dataframe()
        if not data.empty:
            logger.info("Loading symbols from cache...")
            return data

    logger.info(f"Generating symbols ...")
    pro = ts.pro_api(tushare_api_key)
    df_hk = pro.hk_basic()
    df_hk['symbol'] = df_hk['ts_code'].str.replace('.HK', '', regex=False)
    df_hk['exchange'] = 'HKEX'
    df_cn = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,fullname,enname,cnspell,market,exchange,curr_type,list_status,list_date,delist_date,is_hs,act_name,act_ent_type')
    df_all = pd.concat([df_cn, df_hk], ignore_index=True)
    cache.write_dataframe(df_all)
    return df_all