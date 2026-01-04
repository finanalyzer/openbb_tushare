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

EQUITY_INFO_SCHEMA = {
    "ts_code": "TEXT PRIMARY KEY",        # 证券代码 (Security ID)
    "com_name": "TEXT",          # 公司常用名称 (Common Name)
    "isin": "TEXT",                # 国际证券识别号码 (ISIN Code)
    "exchange": "TEXT",          # 证券交易所 (Exchange)
    "introduction": "TEXT",               # 公司描述 (Description)
    "chairman": "TEXT",                   # 董事长 (Chairman)
    "website": "TEXT",                    # 公司网站 (Website URL)
    "office": "TEXT",                     # 总部地址 (Headquarters)
    "city": "TEXT",                       # 城市 (City)
    "province": "TEXT",                   # 省份/州 (Province/State)
    "employees": "INTEGER",               # 员工数量 (Employee Count)
    "list_status": "TEXT",                # 上市状态 (List Status)
    "market": "TEXT",                     # 行业分类 (Industry/Market)
    "com_id": "TEXT",              # 统一社会信用代码 (Business ID)
    "manager": "TEXT",                    # 总经理 (General Manager)
    "secretary": "TEXT",                  # 董事会秘书 (Board Secretary)
    "reg_capital": "REAL",                # 注册资本 (Registered Capital)
    "setup_date": "TEXT",                 # 注册日期 (Registration Date)
    "email": "TEXT",                      # 邮箱 (Email)
    "ann_date": "TEXT",                   # 公告日期 (Announcement Date)
    "business_scope": "TEXT",             # 经营范围 (Business Scope)
    "main_business": "TEXT",              # 主营业务 (Main Business)
    "fullname": "TEXT",          # 公司全称 (Full Legal Name)
    "enname": "TEXT",                     # 英文名称 (English Name)
    "cn_spell": "TEXT",                   # 拼音 (Chinese Spelling)
    "list_date": "TEXT",         # 上市日期 (Listing Date)
    "delist_date": "TEXT",                # 退市日期 (Delisting Date)
    "trade_unit": "REAL",                 # 交易单位 (Trading Unit)
    "curr_type": "TEXT"          # 货币代码 (Currency)
}

def get_hk_data(ts_code: str, pro, cache: TableCache) -> pd.DataFrame:
    a_fields = {
        'ts_code': ts_code,
        'com_id': '',
        'exchange': '',
        'chairman': '',
        'manager': '',
        'secretary': '',
        'reg_capital': 0.0,
        'setup_date': '',
        'province': '',
        'city': '',
        'introduction': '',
        'website': '',
        'email': '',
        'office': '',
        'employees': 0,
        'main_business': '',
        'business_scope': ''
    }

    data_hk = pro.hk_basic(ts_code=ts_code)
    if data_hk.empty:
        logger.warning(f"No equity profile data found for HK stock {ts_code}.")
        return pd.DataFrame()

    data_a = pd.DataFrame([a_fields])
    combined_data = pd.merge(data_hk, data_a, on=['ts_code'], how='outer')
    cache.update_or_insert(combined_data)
    return combined_data

def get_ss_data(ts_code: str, pro, cache: TableCache) -> pd.DataFrame:
    csv_fields = "ts_code,com_name,com_id,exchange,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope"
    data = pro.stock_company(ts_code=ts_code, fields=csv_fields)
    if data.empty:
        logger.warning(f"No equity profile data found for HK stock {ts_code}.")
        return data

    data = data.rename(columns={'com_name': 'name'})

    hk_fields = {
        'ts_code': ts_code,
        'fullname': '',
        'enname': '',
        'cn_spell': '',
        'market': '',
        'list_status': '',
        'list_date': '',
        'delist_date': '',
        'trade_unit': 0.0,
        'isin': '',
        'curr_type': ''
    }
    data_hk = pd.DataFrame([hk_fields])
    combined_data = pd.merge(data_hk, data, on=['ts_code'], how='outer')
    cache.update_or_insert(combined_data)
    return combined_data

def get_equity_profile(ts_code: str, api_key: str = "", use_cache: bool = True) -> pd.DataFrame:
    """
    Retrieves equity profile data from a cache or downloads it from the data source.
    
    Parameters:
        ts_code (str): Tushare stock symbol to fetch data for.
        use_cache (bool): Whether to use cached data or download fresh data.
        api_key (str): Tushare API key for authentication.

    Returns:
        DataFrame: DataFrame containing equity profile data.
    """

    cache = TableCache(EQUITY_INFO_SCHEMA, table_name="equity_profile", primary_key="ts_code")
    _, normalized_ts_code, market = normalize_symbol(ts_code)
    if use_cache:
        filters = {'ts_code': normalized_ts_code}
        data = cache.read_rows(filters)

        if not data.empty:
            logger.info(f"Loading equity profile {normalized_ts_code} from cache...")
            return data

    tushare_api_key = get_api_key(api_key)
    pro = ts.pro_api(tushare_api_key)
    df_data = pd.DataFrame()
    if market == 'HK':
        df_data = get_hk_data(normalized_ts_code, pro, cache)
    else:
        df_data = get_ss_data(normalized_ts_code, pro, cache)

    return df_data

    