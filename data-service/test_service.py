import sys
import os
import json

sys.path.append(os.path.dirname(__file__))

from ai.service import get_company_summary, get_latest_price

def verify_callable_service():
    print("---------------------------------------------------------------------------------")
    print("VERIFYING API MICROSERVICE GATEWAY FOR FASTAPI BOUNDARY")
    print("---------------------------------------------------------------------------------\n")

    # TEST SUBJECT: Apple Inc. (AAPL)
    ticker = "AAPL"
    
    print(f"[SCENARIO 1] Simulating FastAPI requesting latest AI Summary JSON for {ticker}...\n")
    ai_payload = get_company_summary(ticker)
    print(json.dumps(ai_payload, indent=4))
    print("\n" + "="*80 + "\n")

    print(f"[SCENARIO 2] Simulating FastAPI parsing latest daily yfinance Closing Price for {ticker}...\n")
    price_payload = get_latest_price(ticker)
    print(json.dumps(price_payload, indent=4))
    print("\n" + "="*80 + "\n")
    
    print(f"[SCENARIO 3] Simulating Error Guard for an INVALID TICKER...\n")
    invalid_payload = get_company_summary("BADTICKER")
    print(json.dumps(invalid_payload, indent=4))

if __name__ == "__main__":
    verify_callable_service()
