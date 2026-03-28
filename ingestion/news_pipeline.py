# new_pipeline.py
# Smart Finance Intelligence App — News Ingestion Pipeline
# Member 1: Data Ingestion
# Fetches financial news for tracked companies (Indian + US), scores sentiment,
# deduplicates, and stores into Supabase via SQLAlchemy ORM.

import os
import sys
import time
import requests
from datetime import datetime, timezone, timedelta
from collections import deque

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

load_dotenv()

# -------------------------
# Configuration
# -------------------------
NEWS_API_KEY  = os.getenv("NEWS_API_KEY", "").strip()
DATABASE_URL  = os.getenv("DATABASE_URL", "").strip()  # Supabase PostgreSQL connection string

EVERYTHING_URL  = "https://newsapi.org/v2/everything"
UPDATE_INTERVAL = 3600   # 1 hour — matches Task 6 scheduler requirement
MAX_ARTICLES    = 20     # per company per fetch (NewsAPI free: 100 req/day, 12 companies = fine)

# Financial news keywords — covers Indian + US market events
FINANCIAL_KEYWORDS = [
    "earnings", "revenue", "profit", "loss", "quarterly results", "annual report",
    "merger", "acquisition", "IPO", "listing", "stock", "shares", "dividend",
    "CEO", "CFO", "board", "management", "guidance", "forecast", "outlook",
    "debt", "fundraise", "valuation", "investment", "stake", "buyback",
    "SEBI", "RBI", "NSE", "BSE", "SEC", "regulatory", "compliance", "fine", "penalty",
    "inflation", "interest rate", "GDP", "market", "rally", "crash", "correction"
]

# -------------------------
# SQLAlchemy Setup
# -------------------------
engine  = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

# -------------------------
# Timezone (IST)
# -------------------------
def get_ist_tz():
    if ZoneInfo:
        try:
            return ZoneInfo("Asia/Kolkata")
        except Exception:
            pass
    return timezone(timedelta(hours=5, minutes=30))

IST = get_ist_tz()

def to_ist(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat((iso_ts or "").replace("Z", "+00:00"))
        return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return iso_ts or "N/A"

# -------------------------
# Financial Sentiment Scoring
# -------------------------
POSITIVE_WORDS = {
    "profit", "growth", "record", "beat", "outperform", "dividend", "upgrade",
    "expansion", "acquisition", "partnership", "strong", "surge", "rally",
    "recovery", "opportunity", "win", "award", "launch", "innovation", "raise"
}
NEGATIVE_WORDS = {
    "loss", "decline", "miss", "downgrade", "layoff", "restructure", "debt",
    "default", "fine", "penalty", "fraud", "probe", "investigation", "crash",
    "correction", "sell-off", "warning", "risk", "concern", "cut", "reduce",
    "weak", "shortfall", "recall", "lawsuit", "sue"
}

def sentiment_score(title: str, description: str, content: str) -> float:
    """
    Returns float -1.0 (very bearish) to +1.0 (very bullish).
    Word-count approach — no heavy ML deps.
    """
    text = " ".join(filter(None, [title, description, content])).lower()
    score = 0
    for w in POSITIVE_WORDS:
        if w in text:
            score += 1
    for w in NEGATIVE_WORDS:
        if w in text:
            score -= 1
    return round(max(-5, min(5, score)) / 5.0, 3)

def sentiment_label(score: float) -> str:
    """Maps score to bullish/bearish/neutral — used by Task 8 AI module."""
    if score >= 0.2:
        return "bullish"
    elif score <= -0.2:
        return "bearish"
    return "neutral"

# -------------------------
# Article Normalization
# -------------------------
def normalize_article(article: dict, company_id: int) -> dict:
    """
    Converts raw NewsAPI article into the shape matching raw_data_items table.
    Internal fields prefixed with _ are NOT written to DB — only used for console output.
    """
    title       = article.get("title") or ""
    description = article.get("description") or ""
    content     = article.get("content") or ""
    score       = sentiment_score(title, description, content)

    return {
        # --- DB columns ---
        "company_id":   company_id,
        "source_name":  (article.get("source") or {}).get("name", "Unknown"),
        "data_type":    "news",
        "raw_text":     f"{title}. {description}",
        "url":          article.get("url"),
        "published_at": article.get("publishedAt"),
        # --- Internal only (console output, not stored) ---
        "_sentiment_score": score,
        "_sentiment_label": sentiment_label(score),
        "_title_ist":       to_ist(article.get("publishedAt")),
    }

# -------------------------
# NewsAPI Fetch
# -------------------------
def call_newsapi(params: dict) -> list:
    headers = {"X-Api-Key": NEWS_API_KEY}
    try:
        resp = requests.get(EVERYTHING_URL, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [NewsAPI Error] {e}")
        return []
    data = resp.json()
    if data.get("status") != "ok":
        print(f"  [NewsAPI Error] {data.get('message', data)}")
        return []
    return data.get("articles", [])


def fetch_news_for_company(
    company_name: str,
    ticker: str,
    company_id: int,
    seen_urls: deque,
    hours: int = 48
) -> list[dict]:
    """
    Fetches up to MAX_ARTICLES news articles for one company from the last `hours` hours.
    Searches by company name OR ticker — works for both Indian stocks (RELIANCE, TCS)
    and US stocks (AAPL, GOOGL, TSLA).
    Deduplicates against seen_urls deque passed in from the caller.
    Returns list of normalized article dicts ready for DB insert.
    """
    from_ts = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    # Quote both — exact phrase search works better for company names
    query = f'"{company_name}" OR "{ticker}"'

    params = {
        "q":        query,
        "language": "en",
        "sortBy":   "publishedAt",
        "pageSize": MAX_ARTICLES,
        "from":     from_ts,
    }

    raw_articles = call_newsapi(params)

    new_articles = []
    for a in raw_articles:
        url = a.get("url")
        if url and url not in seen_urls:
            seen_urls.append(url)
            new_articles.append(a)

    if not new_articles:
        return []

    return [normalize_article(a, company_id) for a in new_articles]

# -------------------------
# SQLAlchemy DB Write
# -------------------------
def save_articles_to_db(articles: list[dict]) -> int:
    """
    Inserts normalized articles into raw_data_items via SQLAlchemy.
    Strips internal _ fields before insert.
    Returns count of successfully inserted rows.
    """
    if not articles:
        return 0

    DB_COLS = {"company_id", "source_name", "data_type", "raw_text", "url", "published_at"}
    rows    = [{k: v for k, v in a.items() if k in DB_COLS} for a in articles]

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
        return len(rows)
    except Exception as e:
        session.rollback()
        print(f"  [DB Insert Error] {e}")
        return 0
    finally:
        session.close()

# -------------------------
# Load All Companies from DB
# -------------------------
def load_companies() -> list[dict]:
    """
    Reads all rows from the companies table via SQLAlchemy.
    Returns list of dicts: {id, name, ticker, sector}
    """
    session = Session()
    try:
        result = session.execute(
            text("SELECT id, name, ticker, sector FROM companies ORDER BY id")
        )
        return [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"  [DB Error] Could not load companies: {e}")
        return []
    finally:
        session.close()

# -------------------------
# One-shot fetch for a single ticker
# Callable by ai/service.py (Task 9)
# -------------------------
def fetch_once(ticker: str) -> list[dict]:
    """
    Fetches and saves news for one company immediately.
    Designed to be imported and called by ai/service.py when a fresh summary is needed.
    Returns normalized article list.

    Usage from ai/service.py:
        from new_pipeline import fetch_once
        fetch_once("RELIANCE")
        fetch_once("AAPL")
    """
    session = Session()
    try:
        row = session.execute(
            text("SELECT id, name FROM companies WHERE ticker = :t"),
            {"t": ticker}
        ).fetchone()
    finally:
        session.close()

    if not row:
        print(f"  [fetch_once] Ticker '{ticker}' not found in companies table.")
        return []

    company_id   = row.id
    company_name = row.name
    seen_urls    = deque(maxlen=500)

    articles = fetch_news_for_company(company_name, ticker, company_id, seen_urls)
    saved    = save_articles_to_db(articles)
    print(f"  [fetch_once] {ticker}: fetched {len(articles)}, saved {saved} to DB.")
    return articles

# -------------------------
# Live Polling Loop
# Fetches news for ALL companies in DB every UPDATE_INTERVAL seconds.
# Complements the APScheduler in ingestion/scheduler.py (Task 6).
# -------------------------
def live_news_fetcher():
    """
    Polls NewsAPI every UPDATE_INTERVAL seconds for every company in the DB.
    Reads company list dynamically from DB each cycle — no hardcoding.
    Uses a shared seen_urls deque across all cycles to avoid duplicate DB rows.
    Covers both Indian tickers (RELIANCE, TCS, HDFCBANK) and US tickers (AAPL, TSLA, MSFT).
    """
    seen_urls = deque(maxlen=5000)
    cycle     = 0

    print(f"[Pipeline] Live news fetcher started.")
    print(f"[Pipeline] Interval: {UPDATE_INTERVAL // 60} min | DB: {DATABASE_URL[:45]}...")

    while True:
        cycle += 1
        now   = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S %Z")
        print(f"\n{'='*60}")
        print(f"[Cycle {cycle}] {now}")
        print(f"{'='*60}")

        companies = load_companies()
        if not companies:
            print("  No companies in DB. Seed them first (Task 7).")
        else:
            print(f"  Loaded {len(companies)} companies.\n")

        total_fetched = 0
        total_saved   = 0

        for company in companies:
            cid    = company["id"]
            name   = company["name"]
            ticker = company["ticker"]

            articles = fetch_news_for_company(name, ticker, cid, seen_urls)
            saved    = save_articles_to_db(articles)

            total_fetched += len(articles)
            total_saved   += saved

            if articles:
                print(f"  [{ticker}] {len(articles)} new articles (saved {saved}):")
                for a in articles[:3]:
                    label = a["_sentiment_label"].upper()
                    score = a["_sentiment_score"]
                    print(f"    • {a['raw_text'][:75]}...")
                    print(f"      {label} ({score:+.2f}) | {a['source_name']} | {a['_title_ist']}")
            else:
                print(f"  [{ticker}] No new articles.")

        print(f"\n[Cycle {cycle}] Total fetched: {total_fetched} | Saved: {total_saved}")
        print(f"Next cycle in {UPDATE_INTERVAL // 60} minutes...\n")
        time.sleep(UPDATE_INTERVAL)

# -------------------------
# CLI
# -------------------------
def print_usage():
    print("\nUsage:")
    print("  python new_pipeline.py fetch             -> start live polling loop (all companies)")
    print("  python new_pipeline.py once <TICKER>     -> fetch news for one ticker right now")
    print("  python new_pipeline.py list              -> list all companies in DB")
    print("\nExamples:")
    print("  python new_pipeline.py once RELIANCE")
    print("  python new_pipeline.py once AAPL")
    print("  python new_pipeline.py fetch")

if __name__ == "__main__":
    missing = []
    if not NEWS_API_KEY:
        missing.append("NEWS_API_KEY")
    if not DATABASE_URL:
        missing.append("DATABASE_URL")
    if missing:
        print(f"⚠️  Missing env vars: {', '.join(missing)}")
        print("   Add them to your .env file and retry.")
        sys.exit(1)

    if len(sys.argv) >= 2:
        cmd = sys.argv[1].lower()

        if cmd == "fetch":
            live_news_fetcher()

        elif cmd == "once" and len(sys.argv) >= 3:
            fetch_once(sys.argv[2].upper())

        elif cmd == "list":
            companies = load_companies()
            if not companies:
                print("No companies seeded yet.")
            else:
                print(f"\n{'ID':<5} {'Ticker':<12} {'Name':<35} {'Sector'}")
                print("-" * 65)
                for c in companies:
                    print(f"{c['id']:<5} {c['ticker']:<12} {c['name']:<35} {c.get('sector', '')}")
        else:
            print_usage()
    else:
        print_usage()