import logging
import os
from dotenv import load_dotenv

# We must load env vars first
load_dotenv()
logging.basicConfig(level=logging.INFO)

from ingestion.news_fetcher import fetch_news

if __name__ == "__main__":
    print("-" * 50)
    print("TESTING NEWS API V1 PIPELINE")
    print("-" * 50)
    
    if os.getenv("NEWS_API_KEY") == "your_newsapi_key":
        print("❌ Wait! You haven't added your precise NewsAPI key to data-service/.env!")
        print("Please grab one from newsapi.org (free) and set NEWS_API_KEY, then run again.")
    else:
        # Test a US and Indian company to make sure the fetcher operates cleanly
        results = fetch_news(company_name="Tesla, Inc.", ticker="TSLA")
        if results:
            print("\n✅ Successfully Pulled Tesla News:")
            for article in results:
                print(f" -> {article['title']} ({article['source']})")
        else:
            print("\n⚠️ No new Tesla articles pulled (or API failed).")
