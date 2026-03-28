import os
import sys

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import Session
from sqlalchemy import text

COMPANIES = [
    {"name": "Reliance Industries", "ticker": "RELIANCE", "sector": "Conglomerate"},
    {"name": "Infosys", "ticker": "INFY", "sector": "Information Technology"},
    {"name": "TCS", "ticker": "TCS", "sector": "Information Technology"},
    {"name": "HDFC Bank", "ticker": "HDFCBANK", "sector": "Financials"},
    {"name": "Wipro", "ticker": "WIPRO", "sector": "Information Technology"},
    {"name": "Bajaj Finance", "ticker": "BAJFINANCE", "sector": "Financials"},
    {"name": "Apple", "ticker": "AAPL", "sector": "Technology"},
    {"name": "Google", "ticker": "GOOGL", "sector": "Technology"},
    {"name": "Tesla", "ticker": "TSLA", "sector": "Consumer Discretionary"},
    {"name": "Microsoft", "ticker": "MSFT", "sector": "Technology"},
    {"name": "Amazon", "ticker": "AMZN", "sector": "Consumer Discretionary"},
]

def seed_companies():
    session = Session()
    try:
        # We can use ON CONFLICT DO NOTHING if ticker is unique, or just check if it exists.
        # Assuming ticker might not have a UNIQUE constraint natively, we will manually check or use a simple loop.
        for company in COMPANIES:
            exists = session.execute(
                text("SELECT id FROM companies WHERE ticker = :ticker"),
                {"ticker": company["ticker"]}
            ).fetchone()
            
            if not exists:
                session.execute(
                    text("""
                        INSERT INTO companies (ticker, name, sector)
                        VALUES (:ticker, :name, :sector)
                    """),
                    company
                )
                print(f"Inserted {company['name']} ({company['ticker']})")
            else:
                print(f"Company {company['name']} ({company['ticker']}) already exists.")
                
        session.commit()
        print("Seeding complete.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding companies: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_companies()
