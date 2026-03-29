import logging
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_db import SessionLocal, Company
from ingestion.news_fetcher import fetch_news
from ingestion.price_fetcher import fetch_prices
from ingestion.filing_fetcher import fetch_filings
from ingestion.goal_snapshotter import record_goal_snapshots

logger = logging.getLogger(__name__)

def job_fetch_news():
    logger.info("----- STARTING SCHEDULED JOB: Fetch News -----")
    with SessionLocal() as db:
        companies = db.query(Company).all()
        for c in companies:
            fetch_news(company_name=c.name, ticker=c.ticker)
    logger.info("----- FINISHED SCHEDULED JOB: Fetch News -----")

def job_fetch_prices():
    logger.info("----- STARTING SCHEDULED JOB: Fetch Prices -----")
    with SessionLocal() as db:
        companies = db.query(Company).all()
        for c in companies:
            fetch_prices(ticker=c.ticker)
    logger.info("----- FINISHED SCHEDULED JOB: Fetch Prices -----")

def job_fetch_filings():
    logger.info("----- STARTING SCHEDULED JOB: Fetch Filings -----")
    with SessionLocal() as db:
        companies = db.query(Company).all()
        for c in companies:
            fetch_filings(company_name=c.name, ticker=c.ticker)
    logger.info("----- FINISHED SCHEDULED JOB: Fetch Filings -----")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Hook the cron logic to exactly match your Phase 1 intervals
    scheduler.add_job(job_fetch_news, 'interval', hours=1, id='job_news')
    scheduler.add_job(job_fetch_prices, 'interval', hours=6, id='job_prices')
    scheduler.add_job(job_fetch_filings, 'interval', hours=24, id='job_filings')
    scheduler.add_job(record_goal_snapshots, 'interval', hours=24, id='job_snapshots')
    
    scheduler.start()
    logger.info("🚀 APScheduler successfully activated! Background fetchers are humming in parallel.")
