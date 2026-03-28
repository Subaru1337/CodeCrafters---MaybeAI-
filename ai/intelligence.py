import os
import sys
import json
from datetime import datetime, timedelta
import anthropic

# Add parent directory to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL_NAME = "claude-sonnet-4-20250514"

def generate_summary(company_id: int, language: str = 'English') -> dict:
    """
    Queries recent news, filings, and earnings transcripts for a company from raw_data_items,
    calls the Anthropic Claude API to generate a structured AI summary,
    saves the result to processed_summaries, and returns it.
    """
    session = Session()
    try:
        # Check if company exists first
        company = session.execute(
            text("SELECT name FROM companies WHERE id = :id"),
            {"id": company_id}
        ).fetchone()
        
        if not company:
            print(f"Company ID {company_id} not found.")
            return {}
            
        company_name = company.name
        
        # 1. Gather Data (last 48 hours for news, latest for filing/earnings call)
        time_48h_ago = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        
        # We limit news to 10 rows
        news_query = text("""
            SELECT source_name, raw_text, published_at FROM raw_data_items 
            WHERE company_id = :cid AND data_type = 'news' AND published_at >= :t48
            ORDER BY published_at DESC LIMIT 10
        """)
        recent_news = session.execute(news_query, {"cid": company_id, "t48": time_48h_ago}).fetchall()
        
        filing_query = text("""
            SELECT source_name, raw_text, published_at FROM raw_data_items 
            WHERE company_id = :cid AND data_type = 'filing'
            ORDER BY published_at DESC LIMIT 1
        """)
        latest_filing = session.execute(filing_query, {"cid": company_id}).fetchone()
        
        earnings_query = text("""
            SELECT source_name, raw_text, published_at FROM raw_data_items 
            WHERE company_id = :cid AND data_type = 'earnings_call'
            ORDER BY published_at DESC LIMIT 1
        """)
        latest_earnings = session.execute(earnings_query, {"cid": company_id}).fetchone()
        
        # 2. Build Information Block
        context_parts = []
        if recent_news:
            context_parts.append("RECENT NEWS:")
            for row in recent_news:
                context_parts.append(f"- [{row.source_name} on {row.published_at}]: {row.raw_text}")
        if latest_filing:
            context_parts.append(f"\nLATEST FILING [{latest_filing.source_name} on {latest_filing.published_at}]:\n{latest_filing.raw_text}")
        if latest_earnings:
            context_parts.append(f"\nLATEST EARNINGS CALL [{latest_earnings.source_name} on {latest_earnings.published_at}]:\n{latest_earnings.raw_text[:2000]}") # Truncate audio transcript to 2000 chars roughly to save tokens if huge
            
        context_text = "\n".join(context_parts)
        if not context_text.strip():
            context_text = "No recent data found for this company."

        # 3. Call Claude API
        prompt = f"""Respond entirely in {language}.
You are an expert financial analyst. Analyze the provided context for {company_name}.
Context:
{context_text}

Return ONLY valid JSON with exactly the following keys:
- summary: A 3-paragraph executive summary of the company's current situation.
- confidence_score: A float from 0.0 to 1.0 representing your confidence in the data.
- sentiment: Exactly one of 'bullish', 'bearish', or 'neutral'.
- sentiment_score: A float from -1.0 to +1.0.
- conflict_description: A string describing conflicts in the data (e.g., news says bullish but filing says bearish), or 'None' if no conflicting info.
- sources_used: An array of strings containing the source names you relied upon.

Ensure no markdown formatting around the JSON string, just raw valid JSON.
"""

        message = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1000,
            temperature=0.0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Minor clean up in case Claude wraps in markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        ai_data = json.loads(response_text)
        
        # Prepare DB Record
        record = {
            "company_id": company_id,
            "summary_text": ai_data.get("summary", ""),
            "confidence_score": float(ai_data.get("confidence_score", 0.0)),
            "sentiment": ai_data.get("sentiment", "neutral"),
            "sentiment_score": float(ai_data.get("sentiment_score", 0.0)),
            "conflicts_found": ai_data.get("conflict_description", "None").lower() != "none",
            "conflict_description": ai_data.get("conflict_description", "None"),
            "sources_used": json.dumps(ai_data.get("sources_used", [])),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # 4. Save to processed_summaries
        insert_query = text("""
            INSERT INTO processed_summaries
            (company_id, summary_text, confidence_score, sentiment, sentiment_score, conflicts_found, conflict_description, sources_used, generated_at)
            VALUES
            (:company_id, :summary_text, :confidence_score, :sentiment, :sentiment_score, :conflicts_found, :conflict_description, :sources_used, :generated_at)
            RETURNING id
        """)
        
        ret = session.execute(insert_query, record).fetchone()
        session.commit()
        record["id"] = ret.id
        
        print(f"Successfully generated and saved AI summary for {company_name} (ID: {record['id']}).")
        return record
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse Claude JSON response: {e}")
        return {}
    except Exception as e:
        session.rollback()
        print(f"Error generating summary: {e}")
        return {}
    finally:
        session.close()

if __name__ == "__main__":
    print("Test Command:")
    print("python ai/intelligence.py")
    # For testing: generate_summary(1)
