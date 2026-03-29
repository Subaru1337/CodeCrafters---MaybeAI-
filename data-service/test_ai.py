import logging
import os
import json
from dotenv import load_dotenv

# We must load env vars first
load_dotenv()
logging.basicConfig(level=logging.INFO)

from ai.intelligence import generate_company_summary

if __name__ == "__main__":
    print("-" * 65)
    print("TESTING GEMINI-1.5-FLASH AI INTELLIGENCE PIPELINE")
    print("-" * 65)
    
    if os.getenv("GEMINI_API_KEY") == "your_gemini_api_key":
        print("❌ Wait! You haven't added your precise Gemini API key to data-service/.env!")
        print("Grab a free key from Google AI Studio and paste it into GEMINI_API_KEY, then run again.")
    else:
        # Test pulling AAPL which definitely has 2 real SEC filings and possible news from Phase 1 testing!
        print("🧠 Launching context window extraction for Apple Inc. (AAPL)...")
        results = generate_company_summary(ticker="AAPL")
        
        if results:
            print("\n✅ Successfully Generated AI Financial Payload:")
            print("-" * 50)
            print(f"Bull/Bear Sentiment Score: {results['sentiment_score']}/100")
            print(f"Analyst Warning: {results.get('conflict_description', 'N/A')}")
            print("-" * 50)
            print(f"Detailed Markdown Summary:\n\n{results.get('summary_text', 'N/A')}")
        else:
            print("\n⚠️ No AI Payload Generated. Check logs to ensure you have RawData stored or a valid API key.")
