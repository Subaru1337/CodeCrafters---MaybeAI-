import os
import sys
import json
from datetime import datetime, timedelta
import anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL_NAME = "claude-sonnet-4-20250514"

# Mock lists of Indian vs US tickers based on our seed data, for Home Bias detection.
INDIAN_TICKERS = {"RELIANCE", "INFY", "TCS", "HDFCBANK", "WIPRO", "BAJFINANCE"}

def detect_biases(user_id: int) -> dict:
    """
    Detects behavioral biases in a user's portfolio and watchlist
    by querying historical prices and member 2's tables.
    Sends findings to Claude API returning an Investor Behaviour Report.
    """
    session = Session()
    biases_found = []
    
    try:
        # We assume Member 2 created:
        # saved_portfolios(id, user_id, risk_level, target_return_pct, allocations JSON, created_at)
        # watchlist(id, user_id, company_id, added_at)
        
        # 1. Fetch User Data
        portfolio = session.execute(
            text("""
                SELECT risk_level, target_return_pct, allocations
                FROM saved_portfolios WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1
            """), {"uid": user_id}
        ).fetchone()
        
        watchlist_rows = session.execute(
            text("""
                SELECT c.ticker FROM watchlist w
                JOIN companies c ON w.company_id = c.id
                WHERE w.user_id = :uid
            """), {"uid": user_id}
        ).fetchall()
        
        if not portfolio and not watchlist_rows:
            return {
                "biases_found": [],
                "report_text": "No portfolio or watchlist data found for user to analyze biases.",
                "analysed_at": datetime.utcnow().isoformat()
            }
            
        allocations = portfolio.allocations if portfolio and portfolio.allocations else {}
        watchlist_tickers = [r.ticker for r in watchlist_rows]
        
        # All relevant tickers involved in portfolio + watchlist
        all_user_tickers = set(watchlist_tickers)
        for ticker in allocations.keys():
            all_user_tickers.add(ticker)
            
        # 2. OVERCONFIDENCE BIAS
        # risk_level 4-5 AND target_return_pct > 25%
        if portfolio:
            risk = portfolio.risk_level or 0
            target_return = portfolio.target_return_pct or 0.0
            if risk >= 4 and target_return > 25.0:
                biases_found.append("OVERCONFIDENCE")

        # 3. HOME BIAS
        # >70% of watchlist/portfolio from one country
        indian_count = sum(1 for t in all_user_tickers if t in INDIAN_TICKERS)
        us_count = sum(1 for t in all_user_tickers if t not in INDIAN_TICKERS)
        total_assets = len(all_user_tickers)
        
        if total_assets > 0:
            if (indian_count / total_assets) > 0.7 or (us_count / total_assets) > 0.7:
                biases_found.append("HOME BIAS")

        # 4. CONCENTRATION BIAS
        # user repeatedly hits 30% cap on same 2-3 tickers
        # Simplified: check current allocations
        concentrated_tickers = [ticker for ticker, weight in allocations.items() if float(weight) >= 30.0]
        if len(concentrated_tickers) >= 2:
            biases_found.append("CONCENTRATION BIAS")

        # 5. RECENCY BIAS
        # portfolio overweights assets that spiked >20% in 30 days
        time_30d_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        recency_bias_detected = False
        for ticker, weight in allocations.items():
            if float(weight) > 15.0:  # "overweights" generic threshold
                # Get historical prices for last 30 days
                prices = session.execute(
                    text("""
                        SELECT p.close FROM price_history p
                        JOIN companies c ON p.company_id = c.id
                        WHERE c.ticker = :ticker AND p.date >= :t30
                        ORDER BY p.date ASC
                    """), {"ticker": ticker, "t30": time_30d_ago}
                ).fetchall()
                
                if len(prices) >= 2:
                    oldest_price = prices[0].close
                    latest_price = prices[-1].close
                    if oldest_price > 0:
                        spike = (latest_price - oldest_price) / oldest_price
                        if spike > 0.20:
                            recency_bias_detected = True
                            
        if recency_bias_detected:
            biases_found.append("RECENCY BIAS")

        # 6. Generate AI Report
        context_text = f"User Portfolio Allocations: {allocations}\n"
        context_text += f"User Watchlist: {watchlist_tickers}\n"
        if portfolio:
            context_text += f"Risk Level: {portfolio.risk_level}/5 | Target Return: {portfolio.target_return_pct}%\n"
        context_text += f"\nDetected Biases: {', '.join(biases_found) if biases_found else 'None detected'}\n"
        
        prompt = f"""You are a behavioral finance expert. Based on the user's detected biases and portfolio, write a plain-English "Investor Behaviour Report" (2-3 paragraphs). 
Explain the identified biases ({', '.join(biases_found) if biases_found else 'None'}) gently and provide actionable advice to improve their strategy.
Context:
{context_text}

Return entirely raw text. No markdown, no json formatting."""

        message = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        report_text = message.content[0].text.strip()
        
        return {
            "biases_found": biases_found,
            "report_text": report_text,
            "analysed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        session.rollback()
        print(f"Error in detect_biases: {e}")
        return {
            "biases_found": [],
            "report_text": f"Error generating bias report: {str(e)}",
            "analysed_at": datetime.utcnow().isoformat()
        }
    finally:
        session.close()

if __name__ == "__main__":
    print("Testing detect_biases for user_id 1...")
    # detect_biases(1)
