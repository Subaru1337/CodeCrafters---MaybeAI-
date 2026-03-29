import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from db import SessionLocal

def get_available_assets(profile=None):
    """
    Fetches real asset data from price_history table.
    Computes expected returns and covariance matrix from actual price history.
    Falls back to mock data if DB has insufficient data.
    """
    session = SessionLocal()
    try:
        # Step 1 — get all companies with at least 30 days of price history
        result = session.execute(text("""
            SELECT c.id, c.ticker, c.name, c.sector, COUNT(ph.id) as day_count
            FROM companies c
            JOIN price_history ph ON ph.company_id = c.id
            GROUP BY c.id, c.ticker, c.name, c.sector
            HAVING COUNT(ph.id) >= 200
            ORDER BY day_count DESC
        """)).fetchall()

        if not result or len(result) < 3:
            print("WARNING: Not enough price history in DB. Using mock data.")
            return _mock_fallback(profile)

        company_ids = [row[0] for row in result]
        tickers     = [row[1] for row in result]
        sectors     = [row[3] for row in result]

        # Step 2 — fetch last 90 days of close prices for each company
        prices = {}
        for company_id, ticker in zip(company_ids, tickers):
            rows = session.execute(text("""
                SELECT date, close
                FROM price_history
                WHERE company_id = :cid
                ORDER BY date DESC
                LIMIT 365
            """), {"cid": company_id}).fetchall()

            if len(rows) >= 200:
                closes = [float(r[1]) for r in reversed(rows)]
                prices[ticker] = closes

        if len(prices) < 3:
            print("WARNING: Not enough price data. Using mock data.")
            return _mock_fallback(profile)

        # Step 3 — compute daily LOG returns for each ticker (more stable)
        returns_dict = {}
        for ticker, closes in prices.items():
            closes_arr = np.array(closes, dtype=float)
            # log returns are more stable for annualization
            daily_returns = np.diff(np.log(closes_arr))
            # remove any NaN or inf values
            daily_returns = daily_returns[np.isfinite(daily_returns)]
            if len(daily_returns) >= 199:
                returns_dict[ticker] = daily_returns.tolist()

        if len(returns_dict) < 3:
            return _mock_fallback(profile)

        # Step 4 — align lengths (use minimum available days across all tickers)
        min_len = min(len(v) for v in returns_dict.values())
        aligned = {t: v[-min_len:] for t, v in returns_dict.items()}

        asset_names    = list(aligned.keys())
        returns_matrix = np.array([aligned[t] for t in asset_names])

        # Step 5 — annualize expected returns and covariance matrix
        expected_returns = returns_matrix.mean(axis=1) * 252
        cov_matrix       = np.cov(returns_matrix) * 252

        # clip returns to realistic annual range: -30% to +60%
        expected_returns = np.clip(expected_returns, -0.50, 0.80)

        # Step 6 — apply regulatory constraints from profile
        if profile:
            regulatory  = getattr(profile, 'regulatory_constraints', []) or []
            exclude_idx = set()

            for i, ticker in enumerate(asset_names):
                if ('no_crypto' in regulatory or 'No Crypto' in regulatory):
                    if ticker in ('BTC', 'ETH', 'CRYPTO'):
                        exclude_idx.add(i)
                if ('no_foreign_stocks' in regulatory or 'No Foreign Stocks' in regulatory):
                    indian_tickers = {
                        'RELIANCE', 'INFY', 'TCS', 'HDFCBANK',
                        'WIPRO', 'BAJFINANCE', 'ICICIBANK'
                    }
                    if ticker not in indian_tickers:
                        exclude_idx.add(i)

            if exclude_idx:
                keep             = [i for i in range(len(asset_names)) if i not in exclude_idx]
                asset_names      = [asset_names[i] for i in keep]
                expected_returns = expected_returns[keep]
                cov_matrix       = cov_matrix[np.ix_(keep, keep)]

        print(f"Real asset data loaded: {len(asset_names)} assets from price_history")
        return asset_names, expected_returns, cov_matrix

    except Exception as e:
        print(f"ERROR in get_available_assets: {e}. Falling back to mock data.")
        return _mock_fallback(profile)
    finally:
        session.close()


def _mock_fallback(profile=None):
    """
    Fallback mock data — only used if DB has no price history yet.
    """
    assets           = ["SPY","QQQ","EFA","EEM","AGG","LQD","TIP","GLD","VNQ","BTC"]
    expected_returns = np.array([0.08,0.11,0.06,0.07,0.04,0.05,0.03,0.05,0.07,0.40])
    vols             = np.array([0.15,0.20,0.16,0.22,0.05,0.08,0.06,0.15,0.18,0.70])
    corr = np.array([
        [1.00,0.90,0.80,0.70,-0.20,0.30,-0.10,0.10,0.60,0.20],
        [0.90,1.00,0.70,0.65,-0.15,0.25,-0.10,0.10,0.50,0.25],
        [0.80,0.70,1.00,0.75,-0.10,0.20,-0.05,0.15,0.55,0.15],
        [0.70,0.65,0.75,1.00,-0.05,0.15,0.00,0.20,0.45,0.20],
        [-0.20,-0.15,-0.10,-0.05,1.00,0.60,0.70,0.25,0.10,-0.05],
        [0.30,0.25,0.20,0.15,0.60,1.00,0.40,0.15,0.35,0.05],
        [-0.10,-0.10,-0.05,0.00,0.70,0.40,1.00,0.30,0.05,0.00],
        [0.10,0.10,0.15,0.20,0.25,0.15,0.30,1.00,0.10,0.10],
        [0.60,0.50,0.55,0.45,0.10,0.35,0.05,0.10,1.00,0.15],
        [0.20,0.25,0.15,0.20,-0.05,0.05,0.00,0.10,0.15,1.00],
    ])
    cov_matrix = np.outer(vols, vols) * corr

    if profile:
        regulatory  = getattr(profile, 'regulatory_constraints', []) or []
        exclude_idx = set()
        if 'No Crypto' in regulatory or 'no_crypto' in regulatory:
            exclude_idx.add(assets.index("BTC"))
        if exclude_idx:
            keep             = [i for i in range(len(assets)) if i not in exclude_idx]
            assets           = [assets[i] for i in keep]
            expected_returns = expected_returns[keep]
            cov_matrix       = cov_matrix[np.ix_(keep, keep)]

    print("WARNING: Using mock fallback asset data")
    return assets, expected_returns, cov_matrix