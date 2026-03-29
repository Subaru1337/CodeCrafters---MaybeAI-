import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import func
from data_db import engine, PriceHistory, Company

def verify_prices():
    print("Fetching strictly saved Price History from NeonDB...\n")
    with Session(engine) as session:
        # Check raw database count metrics
        companies_with_prices = session.query(
            Company.ticker, func.count(PriceHistory.id)
        ).join(PriceHistory).group_by(Company.ticker).all()
        
        print(f"Total Companies with structured price data stored: {len(companies_with_prices)}")
        for ticker, count in companies_with_prices:
            print(f" -> {ticker}: {count} daily records saved.")
            
        print("\nLast 3 Days of Recorded Data stored in Database:")
        print(f"{'TICKER':<10} | {'DATE':<12} | {'CLOSE':<10} | VOLUME")
        print("-" * 55)
        
        for ticker, _ in companies_with_prices:
            company = session.query(Company).filter(Company.ticker == ticker).first()
            recent_prices = session.query(PriceHistory).filter(PriceHistory.company_id == company.id).order_by(PriceHistory.date.desc()).limit(3).all()
            
            for p in recent_prices:
                print(f"{ticker:<10} | {str(p.date):<12} | {p.close:<10.2f} | {p.volume}")

if __name__ == "__main__":
    verify_prices()
