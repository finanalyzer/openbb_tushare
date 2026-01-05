import os
from dotenv import load_dotenv
from openbb_tushare.models.equity_historical import TushareEquityHistoricalFetcher

if __name__ == "__main__":
    load_dotenv() 
    tushare_api_key = os.environ.get("TUSHARE_API_KEY")
    if tushare_api_key is None:
        raise ValueError("AKSHARE_API_KEY environment variable not set.")
    
    fetcher = TushareEquityHistoricalFetcher()
    test_params = {"symbol": "600325"}

    print("Testing TushareEquityHistoricalFetcher...")
    print(f"Input parameters: {test_params}")

    # Transform the query to see how parameters are processed
    query = fetcher.transform_query(test_params)
    print(f"Transformed query: {query}")

    print("✅ Test completed successfully!")