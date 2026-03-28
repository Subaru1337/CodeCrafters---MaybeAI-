import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine and sessionmaker
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    print("Testing connection to Supabase...")
    try:
        with engine.connect() as conn:
            print("✅ Successfully connected to Supabase PostgreSQL!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
