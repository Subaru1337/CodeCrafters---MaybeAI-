import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import func
from data_db import engine, ProcessedSummary, Company

def verify_ai_payloads():
    print("Fetching strictly saved Generation Summaries from NeonDB...\n")
    with Session(engine) as session:
        # 1. Verification of records logically counting under processed_summaries
        companies_with_ai = session.query(
            Company.ticker, func.count(ProcessedSummary.id)
        ).join(ProcessedSummary).group_by(Company.ticker).all()
        
        print(f"Total Companies with structured AI Intelligence stored: {len(companies_with_ai)}")
        for ticker, count in companies_with_ai:
            print(f" -> {ticker}: {count} AI payload(s) definitively saved.")
            
        print("\nDetailed AI Document Records extracted from Database:")
        print(f"{'TICKER':<10} | {'SENTIMENT':<10} | {'SCORE':<7} | {'DB TEXT CHUNK':<50}")
        print("-" * 85)
        
        # 2. Extract AI text payloads exactly as the DB stores them
        for ticker, _ in companies_with_ai:
            company = session.query(Company).filter(Company.ticker == ticker).first()
            ai_data = session.query(ProcessedSummary).filter(
                ProcessedSummary.company_id == company.id
            ).order_by(ProcessedSummary.generated_at.desc()).limit(1).all()
            
            for f in ai_data:
                short_text = (str(f.summary_text)[:45] + '...') if f.summary_text and len(str(f.summary_text)) > 45 else str(f.summary_text)
                print(f"{ticker:<10} | {str(f.sentiment):<10} | {str(f.sentiment_score):<7} | {short_text:<50}")
                
                print(f" -> Bias Context: {f.conflict_description}\n")

if __name__ == "__main__":
    verify_ai_payloads()
