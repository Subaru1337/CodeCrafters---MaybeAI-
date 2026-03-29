"""
Database configuration and models for Member 1.
"""
import os
import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean, 
    ForeignKey, DateTime, Date, BigInteger, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Member 1 Tables ---

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class RawDataItem(Base):
    __tablename__ = 'raw_data_items'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    source_name = Column(String)
    data_type = Column(String, nullable=False) # 'news', 'price', 'filing', 'research', 'earnings_call'
    raw_text = Column(Text)
    url = Column(String)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    duration_seconds = Column(Integer) # For audio

class ProcessedSummary(Base):
    __tablename__ = 'processed_summaries'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    summary_text = Column(Text, nullable=False)
    confidence_score = Column(Float)
    sentiment = Column(String) # 'bullish', 'bearish', 'neutral'
    sentiment_score = Column(Float)
    conflicts_found = Column(Boolean, default=False)
    conflict_description = Column(Text)
    sources_used = Column(JSON)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

class PriceHistory(Base):
    __tablename__ = 'price_history'
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

# Safely reflect the investment_goals table from Member 2 so SQLAlchemy knows it exists
try:
    from sqlalchemy import Table
    investment_goals_table = Table("investment_goals", Base.metadata, autoload_with=engine)
except Exception as e:
    investment_goals_table = None

class GoalSnapshot(Base):
    __tablename__ = 'goal_snapshots'
    id = Column(Integer, primary_key=True, index=True)
    # If the table from Member 2 exists, strictly enforce the Foreign Key constraint. 
    # Otherwise just use Integer.
    goal_id = Column(Integer, ForeignKey('investment_goals.id') if investment_goals_table is not None else Integer, nullable=False)
    projected_value = Column(Float)
    snapshot_date = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    print("Initializing Database tables (Creating if they don't exist)...")
    # Base.metadata.create_all only attempts to create tables defined in this base.
    # The checkfirst=True prevents it from overriding any existing Member 2 tables.
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Database tables validated/created.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
