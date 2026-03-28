import os
import sys
import time
from apscheduler.schedulers.background import BackgroundScheduler

# Add parent dir to path so we can import db and other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session
from sqlalchemy import text

from ingestion.news_pipeline import fetch_once
from ingestion.price_fetcher import fetch_prices
from ingestion.earnings_fetcher import fetch_earnings_call
from datetime import datetime

def get_all_companies() -> list[dict]:
    session = Session()
    try:
        result = session.execute(text("SELECT id, name, ticker FROM companies")).fetchall()
        return [{"id": row.id, "name": row.name, "ticker": row.ticker} for row in result]
    except Exception as e:
        print(f"Error fetching companies from DB: {e}")
        return []
    finally:
        session.close()

def job_fetch_news():
    print("Starting scheduled news fetch...")
    companies = get_all_companies()
    for comp in companies:
        try:
            fetch_once(comp["ticker"])
        except Exception as e:
            print(f"Error fetching news for {comp['ticker']}: {e}")
    print("Completed scheduled news fetch.")

def job_fetch_prices():
    print("Starting scheduled price fetch...")
    companies = get_all_companies()
    for comp in companies:
        try:
            fetch_prices(comp["ticker"])
        except Exception as e:
            print(f"Error fetching prices for {comp['ticker']}: {e}")
    print("Completed scheduled price fetch.")

def job_fetch_earnings():
    print("Starting quarterly earnings fetch...")
    companies = get_all_companies()
    for comp in companies:
        try:
            fetch_earnings_call(comp["name"], comp["ticker"])
        except Exception as e:
            print(f"Error fetching earnings for {comp['ticker']}: {e}")
    print("Completed scheduled earnings fetch.")

def job_goal_snapshots():
    print("Starting daily goal snapshots...")
    session = Session()
    try:
        goals = session.execute(text("SELECT id, user_id, initial_capital, created_at FROM investment_goals")).fetchall()
        now = datetime.utcnow()
        for goal in goals:
            portfolio = session.execute(
                text("SELECT target_return_pct FROM saved_portfolios WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
                {"uid": goal.user_id}
            ).fetchone()
            
            expected_return = portfolio.target_return_pct / 100.0 if portfolio and portfolio.target_return_pct else 0.08
            days_elapsed = max(0, (now - goal.created_at).days)
            
            projected_value = float(goal.initial_capital) * ((1 + expected_return) ** (days_elapsed / 365.0))
            
            session.execute(
                text("INSERT INTO goal_snapshots (goal_id, projected_value, snapshot_date) VALUES (:goal_id, :proj_val, :snap_date)"),
                {"goal_id": goal.id, "proj_val": projected_value, "snap_date": now.date()}
            )
        session.commit()
        print("Completed daily goal snapshots.")
    except Exception as e:
        session.rollback()
        print(f"Error in goal snapshots job: {e}")
    finally:
        session.close()

def run_scheduler():
    scheduler = BackgroundScheduler()
    
    # Job 1: every 1 hour — call fetch_news for all companies in DB
    scheduler.add_job(job_fetch_news, 'interval', hours=1)
    
    # Job 2: every 6 hours — call fetch_prices for all tickers
    scheduler.add_job(job_fetch_prices, 'interval', hours=6)
    
    # Job 3: every 90 days — call fetch_earnings_call for all companies
    scheduler.add_job(job_fetch_earnings, 'interval', days=90)
    
    # Job 4: every 1 day — goal snapshots
    scheduler.add_job(job_goal_snapshots, 'interval', days=1)
    
    scheduler.start()
    print("Scheduler started. Polling active...")
    
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")

if __name__ == "__main__":
    run_scheduler()
