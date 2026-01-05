"""
Helper functions using AKShare API.
"""
from datetime import (
    date as dateType,
    datetime,
    timedelta
)
import pandas as pd
import akshare as ak
from mysharelib.tools import normalize_symbol

def get_list_date(code: str) -> dateType:
    """
    查询 A 股/港股的上市日期
    code: 对于 A 股请直接给 6 位数字，如 000001
          港股请加 .HK，如 00700.HK
          美股请加 .US，如 AAPL.US
    return: yyyy-mm-dd 字符串
    """
    symbol_b, symbol_f, market = normalize_symbol(code)
    list_date = datetime.now().date()
    if symbol_f.endswith(".HK"):
        # 港股, 2004-06-16
        df = ak.stock_hk_security_profile_em(symbol=code.replace(".HK", ""))
        list_date = datetime.strptime(df.iloc[0]["上市日期"][:10], "%Y-%m-%d")
    else:
        # A 股, 19910403
        df = ak.stock_individual_info_em(symbol=symbol_b)
        list_date = datetime.strptime(str(df[df["item"] == "上市时间"]["value"].iat[0]), "%Y%m%d")

    return list_date.date()


