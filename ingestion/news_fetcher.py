# ingestion/news_fetcher.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from sqlalchemy import text
from db import Session

load_dotenv()

NEWS_API_KEY   = os.getenv("NEWS_API_KEY", "").strip()
EVERYTHING_URL = "https://newsapi.org/v2/everything"

def fetch_news(company_name: str, ticker: str) -> list[dict]:
    """
    Fetches up to 20 recent news articles for a company from NewsAPI.
    Looks up company_id from DB by ticker.
    Saves each article to raw_data_items table via SQLAlchemy.
    Returns list of saved article dicts.
    """
    # Step 1 — get company_id from DB using ticker
    session = Session()
    try:
        row = session.execute(
            text("SELECT id FROM companies WHERE ticker = :t"),
            {"t": ticker}
        ).fetchone()
    finally:
        session.close()

    if not row:
        print(f"  Ticker '{ticker}' not found in companies table.")
        return []

    company_id = row.id

    # Step 2 — fetch from NewsAPI
    from_ts = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    params  = {
        "q":        f'"{company_name}" OR "{ticker}"',
        "language": "en",
        "sortBy":   "publishedAt",
        "pageSize": 20,
        "from":     from_ts,
        "apiKey":   NEWS_API_KEY
    }

    try:
        resp = requests.get(EVERYTHING_URL, params=params, timeout=20)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
    except Exception as e:
        print(f"  NewsAPI error: {e}")
        return []

    if not articles:
        print(f"  No articles found for {ticker}.")
        return []

    # Step 3 — save to DB via SQLAlchemy
    rows = []
    for a in articles:
        rows.append({
            "company_id":   company_id,
            "source_name":  (a.get("source") or {}).get("name", "Unknown"),
            "data_type":    "news",
            "raw_text":     f"{a.get('title', '')}. {a.get('description', '')}",
            "url":          a.get("url"),
            "published_at": a.get("publishedAt"),
        })

    session = Session()
    try:
        session.execute(
            text("""
                INSERT INTO raw_data_items
                    (company_id, source_name, data_type, raw_text, url, published_at)
                VALUES
                    (:company_id, :source_name, :data_type, :raw_text, :url, :published_at)
            """),
            rows
        )
        session.commit()
        print(f"  [{ticker}] Saved {len(rows)} articles to DB.")
    except Exception as e:
        session.rollback()
        print(f"  DB insert error: {e}")
    finally:
        session.close()

    return rows


if __name__ == "__main__":
    results = fetch_news("Infosys", "INFY")
    print(f"Total: {len(results)} articles fetched and saved.")