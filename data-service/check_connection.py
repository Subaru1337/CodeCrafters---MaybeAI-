import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from data_db import engine

def check_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            print(f"\n✅ SUCCESS: Connected to NeonDB! Database returned: {row[0]}\n")
    except Exception as e:
        print(f"\n❌ ERROR: Connection failed. Details:\n{e}\n")

if __name__ == "__main__":
    print("Testing connection to NeonDB...")
    check_connection()
