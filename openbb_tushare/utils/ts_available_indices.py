import os
from dotenv import load_dotenv
import logging

import pandas as pd
import tushare as ts
from openbb_tushare.utils.table_cache import TableCache
from openbb_tushare.utils.tools import setup_logger

TABLE_SCHEMA = {
    "ts_code": "TEXT PRIMARY KEY",    # Unique identifier (TS代码)
    "name": "TEXT NOT NULL",          # Short name (简称)
    "fullname": "TEXT",               # Full index name (指数全称)
    "market": "TEXT NOT NULL",         # Market identifier (市场)
    "publisher": "TEXT",               # Publisher (发布方)
    "index_type": "TEXT",              # Index style classification (指数风格)
    "category": "TEXT",                # Index category (指数类别)
    "base_date": "TEXT",               # Base period (基期, YYYYMMDD format)
    "base_point": "REAL",              # Base points (基点, floating-point)
    "list_date": "TEXT",               # Listing date (发布日期, YYYYMMDD format)
    "weight_rule": "TEXT",             # Weighting method (加权方式)
    "desc": "TEXT",                    # Description (描述)
    "exp_date": "TEXT",                # Expiry date (终止日期, YYYYMMDD format)
    "currency": "TEXT"                 # Currency type (货币)
}

setup_logger()
logger = logging.getLogger(__name__)

def get_available_indices(use_cache: bool = True, api_key : str = "") -> pd.DataFrame:
    if api_key:
        tushare_api_key = api_key
    else:
        load_dotenv() 
        tushare_api_key = os.environ.get("TUSHARE_API_KEY")
    if tushare_api_key is None:
        raise ValueError("TUSHARE_API_KEY environment variable not set.")

    cache = TableCache(TABLE_SCHEMA, table_name="indices", primary_key="ts_code")
    if use_cache:
        data = cache.read_dataframe()
        if not data.empty:
            logger.info("Loading indices from cache...")
            return data

    logger.info(f"Generating new indices data...")
    pro = ts.pro_api(tushare_api_key)
    data = pro.index_basic()
    data["currency"] = "CNY"
    cache.write_dataframe(data)
    return data