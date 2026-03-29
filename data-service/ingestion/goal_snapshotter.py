"""
Task 13: Scheduled Database Job recording Member 2 Goal History.
"""
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_db import SessionLocal, GoalSnapshot, investment_goals_table, engine

logger = logging.getLogger(__name__)

def record_goal_snapshots():
    """
    Chron job scraping User Investment Goals value history into GoalSnapshots table.
    Requires Member 2's FastAPI to have initialized the table structure.
    """
    logger.info("----- STARTING SCHEDULED JOB: Record Goal Snapshots -----")
    
    if investment_goals_table is None:
        logger.warning("Member 2's 'investment_goals' table currently doesn't exist. Skipping Goal Snapshot chron.")
        return
        
    with SessionLocal() as db:
        try:
            with engine.connect() as conn:
                # Query the dynamically reflected Member 2 table securely 
                result = conn.execute(investment_goals_table.select()).fetchall()
                
                count = 0
                today = datetime.utcnow().date()
                
                for row in result:
                    mapping = row._mapping
                    goal_id = mapping["id"]
                    current_value = mapping["current_value"]
                    
                    # Prevent duplicate chron runs on the same strict timezone date
                    exists = db.query(GoalSnapshot).filter(
                        GoalSnapshot.goal_id == goal_id,
                        GoalSnapshot.snapshot_date == today
                    ).first()
                    
                    if not exists:
                        snapshot = GoalSnapshot(
                            goal_id=goal_id,
                            projected_value=float(current_value) if current_value else 0.0,
                            snapshot_date=today
                        )
                        db.add(snapshot)
                        count += 1
                        
                db.commit()
                logger.info(f"Dynamically generated and tracked {count} Daily Goal Snapshots.")
            
        except Exception as e:
            logger.error(f"Failed to record goal snapshots: {e}")
            db.rollback()
    
    logger.info("----- FINISHED SCHEDULED JOB: Record Goal Snapshots -----")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    record_goal_snapshots()
