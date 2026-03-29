"""
Task 8: AI Intelligence Engine using Modern google-genai SDK
"""
import os
import json
import logging
import sys
from datetime import datetime

# Implemented the brand new 2026 python SDK
from google import genai

# Adjust module import path strictly for data-service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_db import SessionLocal, RawDataItem, ProcessedSummary, Company

logger = logging.getLogger(__name__)

def generate_company_summary(ticker: str) -> dict:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key":
        logger.error("WARNING: GEMINI_API_KEY is missing. Please add it to data-service/.env")
        return {}

    # New GenAI Client structure
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    logger.info(f"Synthesizing Gemini AI intelligence for {ticker}...")

    with SessionLocal() as db:
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            logger.error(f"Ticker {ticker} not found in DB.")
            return {}

        items = db.query(RawDataItem).filter(RawDataItem.company_id == company.id).order_by(RawDataItem.published_at.desc()).limit(15).all()
        
        if not items:
            logger.warning(f"Insufficient raw data found for {ticker} to generate a comprehensive AI summary.")
            return {}
            
        context_chunks = []
        for item in items:
            context_chunks.append(f"[{item.data_type.upper()}] {item.source_name} ({item.published_at.date()}): {item.raw_text}")
            
        context_str = "\n".join(context_chunks)
        
        prompt = f"""
        You are an expert Wall Street financial analyst AI. Synthesize the following recent news and corporate filings for '{company.name}' ({company.ticker}).
        
        --- RAW INPUT DATA ---
        {context_str}
        ----------------------
        
        YOUR INSTRUCTIONS:
        1. Write a professional, executive-level financial summary (2-3 paragraphs mapped accurately in markdown formats). Focus on factual business operations, headwinds/tailwinds, and catalysts.
        2. Assign a sentiment_score from 1 (Extreme Bearish) to 100 (Extreme Bullish). 50 is perfectly neutral.
        3. Identify any 'AI Bias/Source Warning'. For example, if the sources are mock data, generic tech news, or overly optimistic PR releases, state that constraint. If the data is robust, state "Sources appear reasonably balanced."
        
        OUTPUT FORMAT (Strictly Pure JSON. Do NOT include ```json Markdown wrappers.):
        {{
            "summary_text": "Your detailed 2-3 paragraph markdown summary here...",
            "sentiment_score": 75,
            "conflict_description": "Your logical bias warning here..."
        }}
        """
        
        try:
            # Shifted to gemini-2.5-flash with the new Client API
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            
            raw_response = response.text.strip()
            
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
                
            result_json = json.loads(raw_response.strip())
            
            existing = db.query(ProcessedSummary).filter(ProcessedSummary.company_id == company.id).first()
            if existing:
                existing.summary_text = result_json.get("summary_text", "")
                existing.sentiment_score = result_json.get("sentiment_score", 50)
                existing.sentiment = "bullish" if existing.sentiment_score > 60 else "bearish" if existing.sentiment_score < 40 else "neutral"
                existing.conflict_description = result_json.get("conflict_description", "")
                existing.generated_at = datetime.utcnow()
            else:
                score = result_json.get("sentiment_score", 50)
                new_summary = ProcessedSummary(
                    company_id=company.id,
                    summary_text=result_json.get("summary_text", ""),
                    sentiment_score=score,
                    sentiment="bullish" if score > 60 else "bearish" if score < 40 else "neutral",
                    conflict_description=result_json.get("conflict_description", "")
                )
                db.add(new_summary)
                
            db.commit()
            logger.info(f"Successfully generated and stored AI intelligence into DB for {ticker}.")
            return result_json
            
        except json.JSONDecodeError as je:
            logger.error(f"Gemini output crashed the JSON parser. Structure invalid.\nError: {je}\nRaw Output: {response.text}")
            return {}
        except Exception as e:
            logger.error(f"Failed to generate intelligence via Gemini for {ticker}: {e}")
            return {}
