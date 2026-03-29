import sys
import os
import json

sys.path.append(os.path.dirname(__file__))

from ai.behavioral import analyze_portfolio_bias

import pprint

def verify_behavioral_logic():
    print("---------------------------------------------------------------------------------")
    print("TESTING BEHAVIORAL BIAS ALGORITHMS FROM AI INTELLIGENCE (TASK 12)")
    print("---------------------------------------------------------------------------------\n")

    mock_user_portfolio = [
        {"ticker": "AAPL", "allocation_pct": 85.0},
        {"ticker": "RELIANCE", "allocation_pct": 15.0} 
    ]
    
    print("Simulating Member 2 sending a highly unbalanced Portfolio:")
    pprint.pprint(mock_user_portfolio)
    print("\nAI BIAS ANALYSIS RESULT:")
    print("=" * 85)
    
    results = analyze_portfolio_bias(mock_user_portfolio)
    pprint.pprint(results)
    print("=" * 85)

if __name__ == "__main__":
    verify_behavioral_logic()
