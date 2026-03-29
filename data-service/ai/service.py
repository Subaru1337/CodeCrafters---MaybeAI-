"""
Task 9 (Updated): Gateway Service Interface for FastAPI
Exposes: get_summary, search_company, get_bias_report, get_company_summary, get_latest_price
"""
import logging
import sys
import os

# Ensure data-service root is always on path, regardless of which directory calls this file
_DATA_SERVICE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DATA_SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _DATA_SERVICE_ROOT)

from data_db import SessionLocal, Company, ProcessedSummary, PriceHistory

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# INT-4 / INT-6 required functions (matching the spec exactly)
# ─────────────────────────────────────────────────────────────

def search_company(query: str) -> list[dict]:
    """
    Search companies by name or ticker (case-insensitive substring match).
    Returns a list of matching company dicts. Empty query returns all companies.
    """
    with SessionLocal() as db:
        if query.strip():
            results = db.query(Company).filter(
                Company.name.ilike(f"%{query}%") | Company.ticker.ilike(f"%{query}%")
            ).limit(10).all()
        else:
            results = db.query(Company).limit(50).all()

        return [
            {
                "id": c.id,
                "ticker": c.ticker,
                "name": c.name,
                "sector": c.sector
            }
            for c in results
        ]


def get_summary(company_id: int, language: str = "English") -> dict:
    """
    Returns the latest AI-generated summary for a given company ID.
    Language param is accepted for future multilingual support (currently English only).
    """
    with SessionLocal() as db:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": f"Company with ID {company_id} not found."}

        summary = db.query(ProcessedSummary).filter(
            ProcessedSummary.company_id == company_id
        ).order_by(ProcessedSummary.generated_at.desc()).first()

        if not summary:
            return {
                "company_id": company_id,
                "ticker": company.ticker,
                "company_name": company.name,
                "summary_text": None,
                "sentiment": None,
                "sentiment_score": None,
                "conflict_description": None,
                "generated_at": None,
                "message": "No AI summary generated yet for this company."
            }

        return {
            "company_id": company_id,
            "ticker": company.ticker,
            "company_name": company.name,
            "summary_text": summary.summary_text,
            "sentiment": summary.sentiment,
            "sentiment_score": summary.sentiment_score,
            "conflict_description": summary.conflict_description,
            "generated_at": summary.generated_at.isoformat()
        }


def get_bias_report(user_id: int) -> dict:
    """
    Fetches user's saved portfolios from the shared DB and runs the behavioral
    bias detector against current AI sentiment scores.
    """
    try:
        from sqlalchemy import Table
        from data_db import engine, Base

        # Safely reflect Member 2's saved_portfolios table
        from sqlalchemy import MetaData
        meta = MetaData()
        meta.reflect(bind=engine, only=["saved_portfolios"])
        portfolios_table = meta.tables.get("saved_portfolios")

        if portfolios_table is None:
            return {"is_biased": False, "bias_warnings": ["Portfolio table not found."]}

        with engine.connect() as conn:
            rows = conn.execute(
                portfolios_table.select().where(portfolios_table.c.user_id == user_id)
            ).fetchall()

        if not rows:
            return {"is_biased": False, "bias_warnings": [], "message": "No portfolios found for this user."}

        # Use the most recent portfolio's allocation JSON
        latest_row = rows[-1]
        allocation = latest_row._mapping.get("allocation", {})

        # Convert allocation dict {"AAPL": 40.0, "INFY": 60.0} → list format
        portfolio_list = [
            {"ticker": ticker, "allocation_pct": pct}
            for ticker, pct in allocation.items()
        ]

        # Run our behavioral bias engine
        from ai.behavioral import analyze_portfolio_bias
        return analyze_portfolio_bias(portfolio_list)

    except Exception as e:
        logger.error(f"Failed to generate bias report for user {user_id}: {e}")
        return {"is_biased": False, "bias_warnings": [], "error": str(e)}


# ─────────────────────────────────────────────────────────────
# Legacy helpers (backwards compatible with existing test scripts)
# ─────────────────────────────────────────────────────────────

def get_company_summary(ticker: str) -> dict:
    """Legacy ticker-based lookup. Prefer get_summary(company_id) for new code."""
    with SessionLocal() as db:
        company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
        if not company:
            return {"error": f"Company '{ticker}' not found."}
        return get_summary(company.id)


def get_latest_price(ticker: str) -> dict:
    with SessionLocal() as db:
        company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
        if not company:
            return {"error": f"Company '{ticker}' not found."}

        recent_price = db.query(PriceHistory).filter(
            PriceHistory.company_id == company.id
        ).order_by(PriceHistory.date.desc()).first()

        if not recent_price:
            return {"error": f"No price history exists for {ticker}."}

        return {
            "ticker": ticker.upper(),
            "close_price": recent_price.close,
            "date": recent_price.date.isoformat(),
            "volume": recent_price.volume
        }
