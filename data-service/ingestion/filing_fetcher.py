"""
Task 5: Fetch Filings — yfinance for Indian stocks, SEC EDGAR for US stocks
"""
import requests
import logging
import yfinance as yf
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_db import SessionLocal, RawDataItem, Company

logger = logging.getLogger(__name__)

INDIAN_TICKERS = {"RELIANCE", "INFY", "TCS", "HDFCBANK", "WIPRO", "BAJFINANCE", "ICICIBANK"}
SEC_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
HEADERS = {"User-Agent": "SmartFinanceHackathonBot admin@example.com"}


def _fetch_indian_via_yfinance(ticker: str, company_name: str) -> list[dict]:
    results = []
    try:
        stock = yf.Ticker(f"{ticker}.NS")
        info = stock.info

        lines = []
        rev = info.get("totalRevenue")
        if rev:
            lines.append(f"Total Revenue: ₹{rev:,.0f}")
        net_income = info.get("netIncomeToCommon")
        if net_income:
            lines.append(f"Net Income: ₹{net_income:,.0f}")
        eps = info.get("trailingEps")
        if eps:
            lines.append(f"Trailing EPS: ₹{eps}")
        pe = info.get("trailingPE")
        if pe:
            lines.append(f"P/E Ratio: {pe:.2f}")
        margin = info.get("profitMargins")
        if margin:
            lines.append(f"Profit Margin: {margin*100:.1f}%")

        if not lines:
            lines.append(f"Financial data for {company_name} retrieved via NSE.")

        text = f"Latest financials for {company_name} ({ticker}.NS). " + " | ".join(lines)
        filing_url = f"https://finance.yahoo.com/quote/{ticker}.NS/financials"

        results.append({
            "title": f"{ticker} Latest Financials (NSE)",
            "url": filing_url,
            "text": text,
            "source": "NSE via Yahoo Finance",
            "date": datetime.utcnow(),
        })
    except Exception as e:
        logger.error(f"yfinance financials failed for {ticker}: {e}")
    return results


def _get_cik(ticker: str) -> str:
    try:
        resp = requests.get(SEC_TICKER_MAP_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for idx, info in data.items():
            if info["ticker"].upper() == ticker.upper():
                return str(info["cik_str"]).zfill(10)
    except Exception as e:
        logger.error(f"Failed to fetch CIK for {ticker}: {e}")
    return ""


def _search_sec_filings(cik: str, ticker: str, company_name: str) -> list[dict]:
    TARGET_FORMS = {"10-K", "10-Q"}

    def _scan_block(block: dict) -> list[dict]:
        # FIX: handles both "recent" wrapper (main file) and flat structure (overflow files)
        recent = block.get("recent", block)
        forms = recent.get("form", [])
        accessions = recent.get("accessionNumber", [])
        dates = recent.get("filingDate", [])
        pri_docs = recent.get("primaryDocument", [])

        results = []
        for i in range(len(forms)):
            if forms[i] in TARGET_FORMS:
                acc_no_dashes = accessions[i].replace("-", "")
                filing_url = (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(cik)}/{acc_no_dashes}/{pri_docs[i]}"
                )
                results.append({
                    "form": forms[i],
                    "url": filing_url,
                    "date": dates[i],
                })
                if len(results) >= 2:
                    break
        return results

    found = []

    try:
        # Pass 1 — main submissions file
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        found = _scan_block(data.get("filings", {}))

        # Pass 2 — overflow files if still nothing found
        if not found:
            for f in data.get("filings", {}).get("files", []):
                overflow_url = f"https://data.sec.gov/submissions/{f['name']}"
                try:
                    r2 = requests.get(overflow_url, headers=HEADERS, timeout=10)
                    r2.raise_for_status()
                    found = _scan_block(r2.json())
                    if found:
                        break
                except Exception as e:
                    logger.warning(f"Failed overflow file {f['name']}: {e}")

    except Exception as e:
        logger.error(f"SEC submissions fetch failed for {ticker}: {e}")

    return found


def fetch_filings(company_name: str, ticker: str) -> list[dict]:
    logger.info(f"Fetching filings for {company_name} ({ticker})...")

    saved_items = []

    with SessionLocal() as db:
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            logger.error(f"Cannot save filings: Ticker {ticker} not found in DB.")
            return []

        # ── BRANCH 1: INDIAN STOCKS via yfinance ────────────────────────────
        if ticker in INDIAN_TICKERS:
            filings = _fetch_indian_via_yfinance(ticker, company_name)
            if not filings:
                logger.warning(f"yfinance returned nothing for {ticker}.")
                return []

            for f in filings:
                exists = db.query(RawDataItem).filter(
                    RawDataItem.url == f["url"],
                    RawDataItem.company_id == company.id
                ).first()
                if not exists:
                    db.add(RawDataItem(
                        company_id=company.id,
                        source_name=f["source"],
                        data_type="filing",
                        raw_text=f["text"],
                        url=f["url"],
                        published_at=f["date"],
                    ))
                    saved_items.append({"title": f["title"], "url": f["url"], "source": f["source"]})
                else:
                    # FIX: already in DB from previous run — still report it so caller knows
                    saved_items.append({"title": f["title"], "url": f["url"], "source": f["source"], "status": "already_exists"})

            db.commit()
            logger.info(f"Saved/found {len(saved_items)} yfinance filings for {ticker}.")
            return saved_items

        # ── BRANCH 2: US STOCKS via SEC EDGAR ───────────────────────────────
        cik = _get_cik(ticker)
        if not cik:
            logger.error(f"Could not map {ticker} to SEC CIK.")
            return []

        filings = _search_sec_filings(cik, ticker, company_name)

        if not filings:
            logger.warning(f"No 10-K/10-Q found on SEC EDGAR for {ticker}.")
            return []

        for f in filings:
            filing_url = f["url"]
            exists = db.query(RawDataItem).filter(
                RawDataItem.url == filing_url,
                RawDataItem.company_id == company.id
            ).first()
            if not exists:
                pub_date = datetime.strptime(f["date"], "%Y-%m-%d")
                db.add(RawDataItem(
                    company_id=company.id,
                    source_name="SEC EDGAR",
                    data_type="filing",
                    raw_text=f"SEC {f['form']} filing for {company_name}. Accessible via EDGAR.",
                    url=filing_url,
                    published_at=pub_date,
                ))
                saved_items.append({"title": f"SEC {f['form']}", "url": filing_url, "source": "SEC EDGAR"})
            else:
                # FIX: already in DB — still report it
                saved_items.append({"title": f"SEC {f['form']}", "url": filing_url, "source": "SEC EDGAR", "status": "already_exists"})

        db.commit()
        logger.info(f"Saved/found {len(saved_items)} SEC filings for {ticker}.")

    return saved_items