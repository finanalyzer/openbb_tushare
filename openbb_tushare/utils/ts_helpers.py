"""
Helper functions using Tushare API.
"""
import tushare as ts
from openbb_tushare.utils.helpers import get_api_key

def get_list_date(ts_code: str, api_key : str = "") -> str:
    """
    ts_code: 000001.SZ / 600000.SH 这种格式
    该函数只支持A股
    """
    tushare_api_key = get_api_key(api_key)

    pro = ts.pro_api(tushare_api_key)
    df = pro.stock_basic(ts_code=ts_code,
                         fields="ts_code,name,list_date")
    return df.iloc[0]["list_date"]   # 形如 19910129