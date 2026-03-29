"""
Task 3: Fetch News from NewsAPI
"""
import os
import requests
import logging
from datetime import datetime

# Adjust module import path strictly for data-service
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_db import SessionLocal, RawDataItem, Company

logger = logging.getLogger(__name__)

NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_news(company_name: str, ticker: str) -> list[dict]:
    # Ensure fresh key load in case it was added recently
    news_api_key = os.getenv("NEWS_API_KEY")
    
    if not news_api_key or news_api_key == "your_newsapi_key":
        logger.error("WARNING: NEWS_API_KEY missing or invalid in .env")
        return []

    logger.info(f"Fetching news for {company_name} ({ticker})...")
    
    # We search by company name or ticker
    params = {
        "q": f'"{company_name}" OR "{ticker}"',
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5, # Keep it strictly to 5 to protect your 100 req/day limit!
        "apiKey": news_api_key
    }
    
    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        saved_items = []
        
        with SessionLocal() as db:
            # 1. We must look up the correct company ID dynamically 
            company = db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                logger.error(f"Cannot save news: Ticker {ticker} not found in DB.")
                return []

            for article in articles:
                url = article.get("url")
                
                # 2. Prevent duplicate article entries
                exists = db.query(RawDataItem).filter(
                    RawDataItem.url == url,
                    RawDataItem.company_id == company.id
                ).first()
                if exists:
                    continue
                
                # 3. Clean up publishing dates
                pub_date_str = article.get("publishedAt")
                published_at = datetime.utcnow()
                if pub_date_str:
                    try:
                        # Convert ISO 2024-03-29T10:00:00Z to pure datetime object
                        parsed = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        published_at = parsed.replace(tzinfo=None) 
                    except ValueError:
                        pass
                
                # We combine title and description for higher AI context later
                raw_text = f"{article.get('title', '')}. {article.get('description', '')}"
                
                new_item = RawDataItem(
                    company_id=company.id,
                    source_name=article.get("source", {}).get("name", "NewsAPI"),
                    data_type="news",
                    raw_text=raw_text,
                    url=url,
                    published_at=published_at
                )
                db.add(new_item)
                
                saved_items.append({
                    "title": article.get("title"),
                    "url": url,
                    "source": article.get("source", {}).get("name")
                })
                
            db.commit()
            logger.info(f"Saved {len(saved_items)} new articles for {ticker} out of {len(articles)} fetched.")
            return saved_items
            
    except Exception as e:
        logger.error(f"Failed to fetch news for {ticker}: {e}")
        return []
