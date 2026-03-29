import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import func
from data_db import engine, RawDataItem, Company

def verify_filings():
    print("Fetching strictly saved Corporate Filings from NeonDB...\n")
    with Session(engine) as session:
        # 1. Verification of records logically counting under 'filing' data type
        companies_with_filings = session.query(
            Company.ticker, func.count(RawDataItem.id)
        ).join(RawDataItem).filter(RawDataItem.data_type == 'filing').group_by(Company.ticker).all()
        
        print(f"Total Companies with structured filing data stored: {len(companies_with_filings)}")
        for ticker, count in companies_with_filings:
            print(f" -> {ticker}: {count} filings definitively saved.")
            
        print("\nDetailed Filing Document Records extracted from Database:")
        print(f"{'TICKER':<10} | {'SOURCE':<15} | {'DB TEXT CHUNK':<35} | URL")
        print("-" * 125)
        
        # 2. Extract textual payloads exactly as the DB stores them
        for ticker, _ in companies_with_filings:
            company = session.query(Company).filter(Company.ticker == ticker).first()
            recent_filings = session.query(RawDataItem).filter(
                RawDataItem.company_id == company.id, 
                RawDataItem.data_type == 'filing'
            ).order_by(RawDataItem.published_at.desc()).limit(3).all()
            
            for f in recent_filings:
                short_text = (f.raw_text[:32] + '...') if len(f.raw_text) > 32 else f.raw_text
                print(f"{ticker:<10} | {f.source_name:<15} | {short_text:<35} | {f.url}")

if __name__ == "__main__":
    verify_filings()
