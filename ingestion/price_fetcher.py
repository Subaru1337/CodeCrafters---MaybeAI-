import os
import requests
from dotenv import load_dotenv
from sqlalchemy import text
import sys

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session

load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def fetch_prices(ticker: str) -> list[dict]:
    """
    Fetches daily price history for a ticker from Alpha Vantage
    and upserts (skips existing) into the price_history table.
    """
    if not ALPHA_VANTAGE_KEY:
        print("Missing ALPHA_VANTAGE_KEY")
        return []
        
    session = Session()
    try:
        # 1. Get company_id for this ticker
        result = session.execute(
            text("SELECT id FROM companies WHERE ticker = :ticker"), 
            {"ticker": ticker}
        ).fetchone()
        
        if not result:
            print(f"Ticker {ticker} not found in companies table.")
            return []
            
        company_id = result.id
        
        # 2. Call Alpha Vantage API
        # Using outputsize=compact to get last 100 data points.
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_KEY,
            "outputsize": "compact"
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            print(f"No price data found for {ticker} in Alpha Vantage response.")
            if "Error Message" in data:
                print(f"API Error: {data['Error Message']}")
            if "Information" in data:
                print(f"API Info: {data['Information']}")
            return []
            
        # 3. Parse and Insert Data
        inserted_count = 0
        parsed_data = []
        
        # The API returns dictionary with dates as keys
        for date_str, daily_data in time_series.items():
            parsed_data.append({
                "company_id": company_id,
                "date": date_str,
                "open": float(daily_data["1. open"]),
                "high": float(daily_data["2. high"]),
                "low": float(daily_data["3. low"]),
                "close": float(daily_data["4. close"]),
                "volume": int(daily_data["5. volume"])
            })
            
        if not parsed_data:
            return []
            
        # Bulk Insert with ON CONFLICT DO NOTHING to skip if company_id+date exists
        query = text("""
            INSERT INTO price_history 
            (company_id, date, open, high, low, close, volume)
            VALUES 
            (:company_id, :date, :open, :high, :low, :close, :volume)
            ON CONFLICT (company_id, date) DO NOTHING
        """)
        
        for row in parsed_data:
            res = session.execute(query, row)
            if res.rowcount > 0:
                inserted_count += 1
                
        session.commit()
        print(f"Successfully inserted {inserted_count} new price records for {ticker}.")
        return parsed_data
        
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching prices for {ticker}: {e}")
        return []
    except Exception as e:
        session.rollback()
        print(f"Error fetching/saving prices for {ticker}: {e}")
        return []
    finally:
        session.close()

if __name__ == "__main__":
    print("Testing fetch_prices for INFY...")
    test_result = fetch_prices('INFY')
    print(f"Fetched {len(test_result)} records in total.")
