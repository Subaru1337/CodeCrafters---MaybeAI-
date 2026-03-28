import os
import requests
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session
from sqlalchemy import text

SEC_USER_AGENT = "FinIntelApp admin@finintel.com"

def fetch_filing(ticker: str, cik: str = None) -> dict:
    """
    Fetches the latest 10-Q or 10-K for US stocks from SEC EDGAR,
    or latest filing for Indian stocks from BSE.
    Saves to raw_data_items table.
    """
    session = Session()
    try:
        # Get company_id
        result = session.execute(
            text("SELECT id FROM companies WHERE ticker = :ticker"), 
            {"ticker": ticker}
        ).fetchone()
        
        if not result:
            print(f"Ticker {ticker} not found in DB.")
            return None
            
        company_id = result.id
        filing_data = None
        
        if cik:
            # US Stock via SEC EDGAR
            cik_padded = cik.zfill(10)
            url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
            headers = {"User-Agent": SEC_USER_AGENT}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                filings = data.get("filings", {}).get("recent", {})
                forms = filings.get("form", [])
                
                # Find the first 10-K or 10-Q
                for i, form in enumerate(forms):
                    if form in ("10-K", "10-Q"):
                        accession_number = filings["accessionNumber"][i].replace("-", "")
                        primary_document = filings["primaryDocument"][i]
                        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession_number}/{primary_document}"
                        
                        filing_data = {
                            "company_id": company_id,
                            "source_name": "SEC EDGAR",
                            "data_type": "filing",
                            "raw_text": f"Form {form} Filed on {filings['filingDate'][i]}",
                            "url": filing_url,
                            "published_at": filings["filingDate"][i]
                        }
                        break
        else:
            # Indian Stock via BSE (placeholder for public endpoint)
            # In a real scenario, this would call BSE India API. 
            # We simulate it fetching a recent corporate announcement.
            filing_data = {
                "company_id": company_id,
                "source_name": "BSE India",
                "data_type": "filing",
                "raw_text": f"Latest Corporate Announcement for {ticker}",
                "url": f"https://www.bseindia.com/stock-share-price/x/y/{ticker}/",
                "published_at": datetime.now().isoformat()
            }
            
        if filing_data:
            # Insert into DB
            query = text("""
                INSERT INTO raw_data_items 
                (company_id, source_name, data_type, raw_text, url, published_at)
                VALUES 
                (:company_id, :source_name, :data_type, :raw_text, :url, :published_at)
            """)
            session.execute(query, filing_data)
            session.commit()
            print(f"Successfully saved {filing_data['source_name']} filing for {ticker}.")
            return filing_data
        else:
            print(f"No suitable filings found for {ticker}.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching filing for {ticker}: {e}")
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving filing for {ticker}: {e}")
        return None
    finally:
        session.close()

if __name__ == "__main__":
    print("Testing fetch_filing for AAPL and RELIANCE...")
    fetch_filing("AAPL", cik="0000320193")
    fetch_filing("RELIANCE")
