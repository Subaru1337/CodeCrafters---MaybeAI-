import logging
from sqlalchemy.orm import Session
from data_db import engine, Company

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMPANIES_TO_SEED = [
    # Indian
    {"ticker": "RELIANCE", "name": "Reliance Industries", "sector": "Conglomerate"},
    {"ticker": "INFY", "name": "Infosys", "sector": "IT Services"},
    {"ticker": "TCS", "name": "Tata Consultancy Services", "sector": "IT Services"},
    {"ticker": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking"},
    {"ticker": "WIPRO", "name": "Wipro", "sector": "IT Services"},
    {"ticker": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financial Services"},
    {"ticker": "ICICIBANK", "name": "ICICI Bank", "sector": "Banking"},   # Added 1
    # US
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "sector": "Automotive"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "sector": "Consumer Cyclical"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"}, # Added 1
    {"ticker": "META", "name": "Meta Platforms, Inc.", "sector": "Technology"}, # Added 1
]

def seed_db():
    logger.info("Checking companies table for seeding...")
    with Session(engine) as session:
        for c_data in COMPANIES_TO_SEED:
            existing_company = session.query(Company).filter(Company.ticker == c_data["ticker"]).first()
            if not existing_company:
                new_c = Company(**c_data)
                session.add(new_c)
                logger.info(f"Seeded: {c_data['name']} ({c_data['ticker']})")
            else:
                logger.debug(f"Skipped: {c_data['ticker']} already exists.")
        
        session.commit()
    logger.info("Database seeding complete. 14 companies verified in the DB.")

if __name__ == "__main__":
    seed_db()
