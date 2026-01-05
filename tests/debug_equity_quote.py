import os
from dotenv import load_dotenv
from openbb_tushare.models.equity_quote import TushareEquityQuoteFetcher

def debug_equity_quote():
    from openbb import obb

    ak_data = obb.equity.price.quote("000002.SZ,000333.SZ,601006.SH,601288.SH", provider='tushare')
    return ak_data.to_dataframe().head()

if __name__ == "__main__":
    load_dotenv() 
    tushare_api_key = os.environ.get("TUSHARE_API_KEY")
    if tushare_api_key is None:
        raise ValueError("AKSHARE_API_KEY environment variable not set.")
    
    fetcher = TushareEquityQuoteFetcher()
    test_params = {"symbol": "600325.SH", "use_cache": True}
    print("Testing TushareEquityQuoteFetcher...")
    print(f"Input parameters: {test_params}")

    # Transform the query to see how parameters are processed
    query = fetcher.test(test_params)
    print(f"Transformed query: {query}")

    print(debug_equity_quote())

    print("✅ Test completed successfully!")    
