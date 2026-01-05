import logging
import pandas as pd
import tushare as ts
from mysharelib.tools import setup_logger
from openbb_tushare.utils.helpers import get_api_key
from mysharelib.tools import normalize_symbol
from openbb_tushare import project_name

setup_logger(project_name)

logger = logging.getLogger(__name__)

def get_one(ts_code : str, use_cache: bool = True, api_key : str = "") -> pd.DataFrame:
    tushare_api_key = get_api_key(api_key)

    logger.info(f"Getting equity quote data for {ts_code}...")
    _, _, market = normalize_symbol(ts_code)
    logger.info(f"Normalized symbol: base={symbol_b}, full={symbol}, market={market}")
    df_data = pd.DataFrame()
    if market == 'HK':
        logger.info(f"Calling pro.rt_hk_k({symbol})")
        pro = ts.pro_api(tushare_api_key)
        df_data = pro.rt_hk_k(symbol)
        if df_data is None or df_data.empty:
            logger.warning(f"No data returned for HK symbol {symbol}")
            return pd.DataFrame()
        # For HK market: select required columns and rename
        df_data = df_data[['ts_code', 'open', 'high', 'low', 'close', 'vol', 'pre_close']]
        df_data = df_data.rename(columns={'vol': 'volume', 'pre_close': 'prev_close'})
    else:
        # Set token for tushare, needed for ts.realtime_quote
        ts.set_token(tushare_api_key)

        logger.info(f"Calling ts.realtime_quote({symbol})")
        ts.set_token(tushare_api_key)
        df_data = ts.realtime_quote(symbol)
        if df_data is None or df_data.empty:
            logger.warning(f"No data returned for symbol {symbol}")
            return pd.DataFrame()
        logger.info(f"Received data with columns: {df_data.columns.tolist()}")
        if df_data is None or df_data.empty:
            logger.warning(f"No data returned from tushare for {ts_code}")
            return pd.DataFrame()
        
        # For non-HK markets: select required columns and rename
        df_data = df_data[['TS_CODE','NAME','BID','ASK','PRICE','OPEN','HIGH','LOW','VOLUME','PRE_CLOSE']]
        df_data = df_data.rename(columns={'TS_CODE':'ts_code', 'NAME':'name', 'BID':'bid', 
                                          'ASK':'ask', 'PRICE': 'last_price', 'OPEN':'open', 
                                          'HIGH':'high', 'LOW':'low', 'VOLUME':'volume', 'PRE_CLOSE': 'prev_close'})
    return df_data
