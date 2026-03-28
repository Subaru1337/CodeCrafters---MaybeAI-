from supabase_client import supabase

companies = [
    {"ticker": "RELIANCE", "name": "Reliance Industries", "sector": "Energy"},
    {"ticker": "INFY", "name": "Infosys", "sector": "IT"},
    {"ticker": "TCS", "name": "TCS", "sector": "IT"},
    {"ticker": "HDFCBANK", "name": "HDFC Bank", "sector": "Banking"},
    {"ticker": "AAPL", "name": "Apple", "sector": "Tech"},
    {"ticker": "GOOGL", "name": "Google", "sector": "Tech"},
]

response = supabase.table("companies").insert(companies).execute()

print(response)