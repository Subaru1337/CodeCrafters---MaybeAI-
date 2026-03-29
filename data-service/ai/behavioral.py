"""
Task 12: Behavioral Biases Module 
Compares user allocations from Member 2 against Member 1's AI Sentiment metrics.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.service import get_company_summary

def analyze_portfolio_bias(portfolio_allocations: list[dict]) -> dict:
    """
    Accepts an array of dicts from Member 2 representing the User's portfolio.
    Example Input:
        [
            {"ticker": "AAPL", "allocation_pct": 85.0},
            {"ticker": "INFY", "allocation_pct": 15.0}
        ]
        
    Output:
        Returns an array of strings detailing psychological/behavioral biases found.
    """
    total_allocation = sum(item.get("allocation_pct", 0) for item in portfolio_allocations)
    
    warnings = []
    
    # Check 1: Diversification Bias
    if len(portfolio_allocations) < 3:
        warnings.append("⚠️ [Under-Diversification Bias]: Your portfolio contains fewer than 3 assets, exposing you to severe un-systematic risk.")

    for asset in portfolio_allocations:
        ticker = asset.get("ticker", "").upper()
        weight = asset.get("allocation_pct", 0)
        
        # Pull our latest internal AI intelligence for this ticker
        summary = get_company_summary(ticker)
        
        if "error" in summary:
            continue
            
        sentiment_score = summary.get("sentiment_score", 50)
        
        # Check 2: Confirmation Bias (Massive allocation against Bearish AI consensus)
        if weight >= 40.0 and sentiment_score < 45.0:
            warnings.append(
                f"🚨 [Confirmation Bias Risk]: You allocated {weight}% of your portfolio to {ticker}, "
                f"but our AI models flagged a Bearish outlook (Score: {sentiment_score}/100) based on recent filings. "
                "Ensure you are not ignoring negative catalysts."
            )
            
        # Check 3: FOMO Bias (Massive allocation into highly generic Bullish consensus without safety)
        if weight >= 60.0 and sentiment_score > 75.0:
            warnings.append(
                f"⚠️ [Herd/FOMO Risk]: {ticker} makes up {weight}% of your holdings. While the AI consensus is highly Bullish, "
                "such extreme concentration indicates performance-chasing behavior. Diversification is recommended."
            )

    return {
        "is_biased": len(warnings) > 0,
        "bias_warnings": warnings
    }
