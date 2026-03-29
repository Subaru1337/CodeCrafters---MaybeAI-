import sys
import os

# Absolute path resolution — works regardless of CWD when uvicorn starts
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))           # api-service/routers/
_API_ROOT  = os.path.dirname(_THIS_DIR)                            # api-service/
_DATA_ROOT = os.path.join(os.path.dirname(_API_ROOT), "data-service")  # ../data-service/

if _DATA_ROOT not in sys.path:
    sys.path.insert(0, _DATA_ROOT)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone

import auth
import models
from db import get_db
from ai.service import get_summary, search_company, get_bias_report

router = APIRouter(
    prefix="/research",
    tags=["Research & Intelligence"]
)

# ─────────────────────────────────────────────────────────────
# GET /research/search?q={query}
# ─────────────────────────────────────────────────────────────

@router.get("/search")
def search_companies(
    q: str = Query(..., min_length=1, description="Search query for company name or ticker"),
    current_user: models.User = Depends(auth.get_current_user)
):
    results = search_company(q)
    if not results:
        return {"results": [], "message": f"No companies found matching '{q}'"}
    return {"results": results, "count": len(results)}


# ─────────────────────────────────────────────────────────────
# GET /research/summary/{company_id}
# ─────────────────────────────────────────────────────────────

@router.get("/summary/{company_id}")
def get_company_intelligence(
    company_id: int,
    language: Optional[str] = Query("English", description="Language for the summary (default: English)"),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = get_summary(company_id, language)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ─────────────────────────────────────────────────────────────
# GET /research/companies
# ─────────────────────────────────────────────────────────────

@router.get("/companies")
def list_all_companies(
    current_user: models.User = Depends(auth.get_current_user)
):
    results = search_company("")
    return {"results": results, "count": len(results)}


# ─────────────────────────────────────────────────────────────
# GET /research/news  ← NEW: replaces hardcoded frontend headlines
# Reads real news from raw_data_items table (fetched by news_fetcher.py)
# ─────────────────────────────────────────────────────────────

@router.get("/news")
def get_latest_news(
    limit: int = Query(20, description="Number of news items to return"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the latest news articles from the raw_data_items table.
    These are real articles fetched by the news_fetcher scheduler.
    """
    from data_db import RawDataItem, Company, SessionLocal

    articles = []

    try:
        with SessionLocal() as data_db:
            rows = (
                data_db.query(RawDataItem, Company)
                .join(Company, RawDataItem.company_id == Company.id)
                .filter(RawDataItem.data_type == "news")
                .order_by(desc(RawDataItem.published_at))
                .limit(limit)
                .all()
            )

            for item, company in rows:
                # Format time as relative string
                time_str = _relative_time(item.published_at)

                articles.append({
                    "id": str(item.id),
                    "title": item.raw_text[:200] if item.raw_text else "No title",
                    "source": item.source_name or "News",
                    "time": time_str,
                    "tag": _classify_tag(item.raw_text, item.url, company.sector),
                    "url": item.url or None,
                })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

    return {"articles": articles, "count": len(articles)}

def _classify_tag(text: str, url: str, fallback_sector: str) -> str:
    """Classify news into a display tag based on headline keywords."""
    combined = ((text or "") + " " + (url or "")).lower()
    if any(w in combined for w in ["rbi", "fed", "rate", "inflation", "gdp", "macro"]):
        return "Macro"
    if any(w in combined for w in ["sebi", "sec", "regulation", "compliance", "filing"]):
        return "Regulation"
    if any(w in combined for w in ["nasdaq", "s&p", "dow", "nifty", "sensex", "index"]):
        return "Markets"
    if any(w in combined for w in ["bond", "yield", "debt", "fixed income", "treasury"]):
        return "Fixed Income"
    if any(w in combined for w in ["crypto", "bitcoin", "ethereum", "blockchain"]):
        return "Crypto"
    if any(w in combined for w in ["earnings", "profit", "revenue", "quarterly", "results"]):
        return "Earnings"
    if any(w in combined for w in ["merger", "acquisition", "ipo", "deal"]):
        return "M&A"
    return fallback_sector or "Markets"
def _relative_time(dt: datetime) -> str:
    """Convert a datetime to a human-readable relative string like '2h ago'."""
    if not dt:
        return "recently"
    try:
        now = datetime.now(timezone.utc)
        # Handle naive datetimes from DB
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        elif seconds < 604800:
            return f"{seconds // 86400}d ago"
        else:
            return dt.strftime("%b %d")
    except Exception:
        return "recently"