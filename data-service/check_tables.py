import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from data_db import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    tables = [row[0] for row in result]
    print(f"\nTables in NeonDB right now: {tables}\n")
