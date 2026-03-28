import numpy as np

def get_available_assets(profile=None):
    """
    Returns mock asset data (expected returns, covariance matrix, asset names) 
    until Member 1 provides the real DB connections to price_history.
    
    Args:
        profile: The user's InvestorProfile model to optionally filter assets 
                 based on regulatory or risk constraints.
                 
    Returns:
        tuple: (asset_names: list, expected_returns: np.ndarray, cov_matrix: np.ndarray)
    """
    # 1. Mock asset universe (10 representative ETFs / assets)
    assets = [
        "SPY",   # US Large Cap Equity
        "QQQ",   # US Tech Equity
        "EFA",   # International Developed Equity
        "EEM",   # Emerging Markets Equity
        "AGG",   # US Core Bonds
        "LQD",   # US Corporate Bonds
        "TIP",   # US Treasury Inflation-Protected Securities
        "GLD",   # Gold
        "VNQ",   # Real Estate
        "BTC"    # Crypto
    ]
    
    # 2. Mock annualized expected returns (mu)
    expected_returns = np.array([
        0.08,  # SPY   (8%)
        0.11,  # QQQ   (11%)
        0.06,  # EFA   (6%)
        0.07,  # EEM   (7%)
        0.04,  # AGG   (4%)
        0.05,  # LQD   (5%)
        0.03,  # TIP   (3%)
        0.05,  # GLD   (5%)
        0.07,  # VNQ   (7%)
        0.40   # BTC   (40%)
    ])
    
    # 3. Mock annualized standalone volatilities
    vols = np.array([0.15, 0.20, 0.16, 0.22, 0.05, 0.08, 0.06, 0.15, 0.18, 0.70])
    
    # 4. Mock Correlation Matrix (Scale -1 to 1)
    corr = np.array([
    #    SPY   QQQ   EFA   EEM   AGG   LQD   TIP   GLD   VNQ   BTC
        [1.00, 0.90, 0.80, 0.70,-0.20, 0.30,-0.10, 0.10, 0.60, 0.20], # SPY
        [0.90, 1.00, 0.70, 0.65,-0.15, 0.25,-0.10, 0.10, 0.50, 0.25], # QQQ
        [0.80, 0.70, 1.00, 0.75,-0.10, 0.20,-0.05, 0.15, 0.55, 0.15], # EFA
        [0.70, 0.65, 0.75, 1.00,-0.05, 0.15, 0.00, 0.20, 0.45, 0.20], # EEM
        [-0.20,-0.15,-0.10,-0.05, 1.00, 0.60, 0.70, 0.25, 0.10,-0.05], # AGG
        [0.30, 0.25, 0.20, 0.15, 0.60, 1.00, 0.40, 0.15, 0.35, 0.05], # LQD
        [-0.10,-0.10,-0.05, 0.00, 0.70, 0.40, 1.00, 0.30, 0.05, 0.00], # TIP
        [0.10, 0.10, 0.15, 0.20, 0.25, 0.15, 0.30, 1.00, 0.10, 0.10], # GLD
        [0.60, 0.50, 0.55, 0.45, 0.10, 0.35, 0.05, 0.10, 1.00, 0.15], # VNQ
        [0.20, 0.25, 0.15, 0.20,-0.05, 0.05, 0.00, 0.10, 0.15, 1.00], # BTC
    ])
    
    # 5. Calculate final Covariance Matrix: Sigma = Diag(vols) * Corr * Diag(vols)
    cov_matrix = np.outer(vols, vols) * corr
    
    # 6. Apply mock constraints (E.g. filter out BTC if too risky or legally forbidden)
    if profile:
        risk_level = getattr(profile, 'risk_level', 3)
        regulatory = getattr(profile, 'regulatory_constraints', []) or []
        
        exclude_indices = set()
        
        if risk_level < 3 or 'No Crypto' in regulatory:
            exclude_indices.add(assets.index("BTC"))
            
        if exclude_indices:
            keep_indices = [i for i in range(len(assets)) if i not in exclude_indices]
            assets = [assets[i] for i in keep_indices]
            expected_returns = expected_returns[keep_indices]
            cov_matrix = cov_matrix[np.ix_(keep_indices, keep_indices)]
            
    return assets, expected_returns, cov_matrix
