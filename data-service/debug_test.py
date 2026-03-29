import sys, os, yfinance as yf, requests
sys.path.append(os.path.abspath('.'))

# --- Test RELIANCE yfinance directly ---
print('=== RELIANCE yfinance test ===')
try:
    stock = yf.Ticker('RELIANCE.NS')
    info = stock.info
    print('info keys sample:', list(info.keys())[:10])
    print('totalRevenue:', info.get('totalRevenue'))
    print('trailingEps:', info.get('trailingEps'))
except Exception as e:
    print('yfinance ERROR:', e)

print()

# --- Test SEC overflow for AAPL ---
print('=== AAPL SEC overflow test ===')
HEADERS = {'User-Agent': 'SmartFinanceHackathonBot admin@example.com'}
cik = '0000320193'
url = f'https://data.sec.gov/submissions/CIK{cik}.json'
r = requests.get(url, headers=HEADERS, timeout=10)
data = r.json()
overflow_files = data.get('filings', {}).get('files', [])
print('Overflow files:', overflow_files)

for f in overflow_files[:2]:
    overflow_url = f"https://data.sec.gov/submissions/{f['name']}"
    print('Fetching:', overflow_url)
    r2 = requests.get(overflow_url, headers=HEADERS, timeout=10)
    data2 = r2.json()
    forms = data2.get('form', [])
    print('Forms in this file (first 10):', forms[:10])
    tenk = [x for x in forms if x in ('10-K', '10-Q')]
    print('10-K/10-Q found:', tenk[:3])
    if tenk:
        break