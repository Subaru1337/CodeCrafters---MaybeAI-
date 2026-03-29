import cvxpy as cp
import numpy as np

# Volatility caps corresponding to user's risk level (1 to 5)
VOLATILITY_CAPS = {
    1: 0.08,  # 8%
    2: 0.12,  # 12%
    3: 0.16,  # 16%
    4: 0.22,  # 22%
    5: 0.30   # 30%
}

def optimize_portfolio(profile, asset_names, expected_returns, cov_matrix):
    """
    Optimizes the portfolio allocation based on the investor profile constraint using cvxpy.
    
    Args:
        profile: InvestorProfile model instance (or a dict-like object with risk_level).
        asset_names (list): List of asset ticker symbols (length n).
        expected_returns (np.array): numpy array of expected returns (length n).
        cov_matrix (np.array): numpy 2D array covariance matrix (n x n).
        
    Returns:
        dict: Containing the optimal allocation weights mapping, expected portfolio return, 
              expected portfolio volatility, and sharpe ratio.
              Returns None if the solver cannot find a feasible solution.
    """
    n = len(asset_names)
    
    # 1. Define the optimization variables (weights for each asset)
    w = cp.Variable(n)
    
    # 2. Extract profile constraints
    try:
        risk_level = profile.risk_level
    except AttributeError:
        # Fallback if profile is a dict (e.g., from What-If simulation)
        risk_level = profile.get("risk_level", 3)
        
    vol_cap = VOLATILITY_CAPS.get(risk_level, 0.16)
    
    # 3. Define the objective (Maximize expected return)
    objective = cp.Maximize(expected_returns @ w)
    
    # 4. Define the strict requirements/constraints
    constraints = [
        cp.sum(w) == 1,                               # Must be fully invested (sum=100%)
        w >= 0,                                       # No shorting allowed
        w <= 0.30,                                    # Max 30% allocation per single asset
        cp.quad_form(w, cov_matrix) <= vol_cap**2     # Portfolio Variance <= (Volatility Cap)^2
    ]
    
    # 5. Formulate and solve the convex optimization problem
    prob = cp.Problem(objective, constraints)
    
    try:
        # Let cvxpy auto-select the best available solver (Clarabel or SCS)
        prob.solve() 
    except Exception as e:
        print(f"Solver encountered an error: {e}")
        return None
        
    if prob.status not in ["optimal", "optimal_inaccurate"]:
        print(f"No feasible portfolio found for Risk Level {risk_level} with max vol {vol_cap}")
        return None
        
    # 6. Extract and clean results
    weights = w.value
    # Eliminate tiny floating point anomalies (e.g. -1e-12 -> 0)
    weights = np.maximum(weights, 0)
    # Re-normalize just in case
    weights /= np.sum(weights) 
    
    # Format allocation to percentages and drop assets with < 0.1% allocation
    allocation = {
        asset_names[i]: round(float(weights[i]) * 100, 2) 
        for i in range(n) if weights[i] > 0.001
    }
    
    port_return = float(expected_returns @ weights)
    port_vol = float(np.sqrt(weights.T @ cov_matrix @ weights))
    # Assuming risk-free rate of roughly 0% for simple Sharpe Ratio formulation here
    sharpe_ratio = port_return / port_vol if port_vol > 0 else 0
    
    return {
        "allocation": allocation,
        "expected_return": port_return,
        "expected_volatility": port_vol,
        "sharpe_ratio": sharpe_ratio
    }
