"""
Task 4: Fetch Prices using yfinance (No API keys needed)
"""
import yfinance as yf
import logging
from datetime import datetime
import sys
import os

# Adjust module import path strictly for data-service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_db import SessionLocal, PriceHistory, Company

logger = logging.getLogger(__name__)

INDIAN_TICKERS = {"RELIANCE", "INFY", "TCS", "HDFCBANK", "WIPRO", "BAJFINANCE", "ICICIBANK"}

def fetch_prices(ticker: str) -> list[dict]:
    logger.info(f"Fetching 3-month price history for {ticker} from yfinance...")
    
    # 1. Indian Stock Routing (.NS)
    query_ticker = ticker
    if ticker in INDIAN_TICKERS:
        query_ticker = f"{ticker}.NS"

    try:
        stock = yf.Ticker(query_ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            logger.warning(f"No price history found for {query_ticker}.")
            return []
            
        saved_items = []
        
        with SessionLocal() as db:
            company = db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                logger.error(f"Cannot save prices: Ticker {ticker} not found in DB.")
                return []

            for date_idx, row in hist.iterrows():
                # Extract pure Python date object from pandas DatetimeIndex
                date_obj = date_idx.date()
                
                open_val = float(row['Open'])
                high_val = float(row['High'])
                low_val  = float(row['Low'])
                close_val= float(row['Close'])
                volume_val= int(row['Volume'])
                
                # 2. Perfect UPSERT behavior algorithm
                existing_record = db.query(PriceHistory).filter(
                    PriceHistory.company_id == company.id,
                    PriceHistory.date == date_obj
                ).first()
                
                if existing_record:
                    existing_record.open = open_val
                    existing_record.high = high_val
                    existing_record.low = low_val
                    existing_record.close = close_val
                    existing_record.volume = volume_val
                else:
                    new_rec = PriceHistory(
                        company_id=company.id,
                        date=date_obj,
                        open=open_val,
                        high=high_val,
                        low=low_val,
                        close=close_val,
                        volume=volume_val
                    )
                    db.add(new_rec)
                    
                saved_items.append({
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "close": close_val,
                    "volume": volume_val
                })
                
            db.commit()
            logger.info(f"Successfully upserted {len(saved_items)} daily price records for {ticker}.")
            return saved_items
            
    except Exception as e:
        logger.error(f"Failed to fetch prices for {ticker}: {e}")
        return []
