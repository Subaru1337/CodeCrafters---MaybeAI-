import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import db and other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session
from sqlalchemy import text
from ai.intelligence import generate_summary
from ai.bias_detector import detect_biases

def get_summary(company_id: int, language: str = 'English') -> dict:
    """
    Retrieves the AI-generated intelligence summary for a given company.
    If a summary was generated in the last 6 hours, it returns the cached version from the database.
    Otherwise, it triggers a fresh generation by calling Anthropic Claude API.

    Args:
        company_id (int): ID of the company to summarize (from 'companies' table).
        language (str): Target language for the summary (default is 'English').

    Returns:
        dict: The summary data including summary_text, sentiment, confidence_score, and conflicts.
    """
    session = Session()
    try:
        time_6h_ago = (datetime.utcnow() - timedelta(hours=6)).isoformat()
        
        # Check if there is a recent summary in the last 6 hours
        query = text("""
            SELECT id, summary_text, confidence_score, sentiment, sentiment_score, 
                   conflicts_found, conflict_description, sources_used, generated_at
            FROM processed_summaries
            WHERE company_id = :cid AND generated_at >= :t6h
            ORDER BY generated_at DESC LIMIT 1
        """)
        
        row = session.execute(query, {"cid": company_id, "t6h": time_6h_ago}).fetchone()
        
        if row:
            import json
            return {
                "id": row.id,
                "summary_text": row.summary_text,
                "confidence_score": row.confidence_score,
                "sentiment": row.sentiment,
                "sentiment_score": row.sentiment_score,
                "conflicts_found": row.conflicts_found,
                "conflict_description": row.conflict_description,
                "sources_used": json.loads(row.sources_used) if row.sources_used else [],
                "generated_at": str(row.generated_at),
                "cached": True
            }
    except Exception as e:
        print(f"Error reading summary from DB: {e}")
    finally:
        session.close()

    # If no recent row found or error occurred, generate a fresh summary
    fresh_summary = generate_summary(company_id, language)
    fresh_summary["cached"] = False
    return fresh_summary

def search_company(query: str) -> list[dict]:
    """
    Searches for companies in the database by matching the query against company names or tickers.
    Uses case-insensitive substring matching (ILIKE).

    Args:
        query (str): The search string (e.g., 'Apple' or 'AAPL').

    Returns:
        list[dict]: A list of matching companies with keys: id, name, ticker, and sector.
    """
    if not query or len(query.strip()) == 0:
        return []
        
    session = Session()
    try:
        search_term = f"%{query.strip()}%"
        sql = text("""
            SELECT id, name, ticker, sector FROM companies
            WHERE name ILIKE :q OR ticker ILIKE :q
            ORDER BY id
        """)
        results = session.execute(sql, {"q": search_term}).fetchall()
        
        return [
            {
                "id": row.id,
                "name": row.name,
                "ticker": row.ticker,
                "sector": row.sector
            } for row in results
        ]
    except Exception as e:
        print(f"Error searching companies: {e}")
        return []
    finally:
        session.close()

def get_bias_report(user_id: int) -> dict:
    """
    Generates an Investor Behaviour Report summarizing the user's trading pattern biases
    such as recency bias, home bias, concentration bias, and overconfidence.

    Args:
        user_id (int): ID of the user whose portfolio and actions will be analyzed.

    Returns:
        dict: Behavioral analysis containing biases_found, report_text, and analysed_at.
    """
    return detect_biases(user_id)
