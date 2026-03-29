import logging

logging.basicConfig(level=logging.INFO)

from ingestion.price_fetcher import fetch_prices

if __name__ == "__main__":
    print("-" * 50)
    print("TESTING YFINANCE PRICE PIPELINE")
    print("-" * 50)
    
    # Test an Indian company to verify the .NS suffix routing works
    print("\nFetching Reliance Industries (Indian Ticker)...")
    results = fetch_prices(ticker="RELIANCE")
    
    if results:
        print(f"\n✅ Successfully pulled {len(results)} days of historic prices!")
        print(f"Latest Recorded Close Price: ₹{results[-1]['close']:.2f} on {results[-1]['date']}")
    else:
        print("\n⚠️ No prices pulled. Check above logs for issues.")
        
    print("\n" + "="*50)
    
    # Test a US company to confirm neutral routing works
    print("\nFetching Apple (US Ticker)...")
    results_us = fetch_prices(ticker="AAPL")
    if results_us:
        print(f"\n✅ Successfully pulled {len(results_us)} days of historic prices for AAPL!")
        print(f"Latest Recorded Close Price: ${results_us[-1]['close']:.2f} on {results_us[-1]['date']}")
