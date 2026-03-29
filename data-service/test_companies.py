import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from data_db import engine, Company

def verify_companies():
    print("Fetching seeded companies from NeonDB...\n")
    with Session(engine) as session:
        companies = session.query(Company).all()
        
        print(f"Total Companies in DB: {len(companies)}\n")
        print(f"{'ID':<5} | {'TICKER':<15} | {'NAME':<30} | SECTOR")
        print("-" * 80)
        
        for c in companies:
            print(f"{c.id:<5} | {c.ticker:<15} | {c.name:<30} | {c.sector}")

if __name__ == "__main__":
    verify_companies()
