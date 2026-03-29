import logging
import sys
import os

logging.basicConfig(level=logging.INFO)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingestion.filing_fetcher import fetch_filings

if __name__ == "__main__":
    print("-" * 55)
    print("TESTING HYBRID SEC/BSE CORPORATE FILING PIPELINE")
    print("-" * 55)
    
    # 1. Test Indian Stack fallback (BSE/NSE Mock)
    print("\n[SCENARIO 1] Fetching Reliance Industries (Indian Ticker)...")
    results_ind = fetch_filings(company_name="Reliance Industries", ticker="RELIANCE")
    if results_ind:
        print(f"\n✅ Indian Branch Triggered! Pulled: {len(results_ind)} logic records.")
        for res in results_ind:
            print(f" -> {res['title']} | {res['url']}")
    
    print("\n" + "="*55)
    
    # 2. Test US Stack dynamic targeting (SEC EDGAR Live Database)
    print("\n[SCENARIO 2] Fetching Apple (US Ticker)...")
    results_us = fetch_filings(company_name="Apple Inc.", ticker="AAPL")
    if results_us:
        print(f"\n✅ US SEC EDGAR Branch Triggered! Pulled: {len(results_us)} Live SEC Documents.")
        for res in results_us:
            print(f" -> {res['title']} | {res['url']}")
            
    print("\nPipeline tests complete.")
