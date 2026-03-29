"""
Main entry point for data-service.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from data_db import init_db
from ingestion.scheduler import start_scheduler
import time

if __name__ == "__main__":
    logger.info("Starting Data Service (Member 1)...")
    init_db()
    db_url = os.getenv("DATABASE_URL", "")
    masked_url = db_url.replace(db_url.split('@')[0].split(':')[-1], "********") if '@' in db_url else db_url
    logger.info(f"Loaded DB URL: {masked_url}")

    logger.info("Firing up background Data Ingestion jobs...")
    start_scheduler()

    try:
        # Halt the main thread alive indefinitely to allow APScheduler daemons to spin
        logger.info("Data Service continuously active. Press Ctrl+C to stop.")
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Data Service forcefully shutdown by User.")
