"""
Verification script for Task 13: Goal Snapshot Scheduler Job
Seeds a dummy investment goal, runs the snapshot job, then checks the DB.
"""
import sys
import os
import logging
from datetime import date, datetime

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from data_db import engine, SessionLocal, GoalSnapshot, investment_goals_table

def verify_goal_snapshots():
    print("-" * 70)
    print("VERIFYING TASK 13: GOAL SNAPSHOT SCHEDULER JOB")
    print("-" * 70)

    if investment_goals_table is None:
        print("❌ ERROR: investment_goals table not found. Member 2's API must run first.")
        return

    # ----------------------------------------------------------------
    # STEP 1: Check if there are real goals in the DB already first
    # ----------------------------------------------------------------
    with engine.connect() as conn:
        existing_goals = conn.execute(investment_goals_table.select()).fetchall()

    print(f"\n[Step 1] Live investment_goals rows found: {len(existing_goals)}")

    # ----------------------------------------------------------------
    # STEP 2: Insert a synthetic test goal so we have something to snapshot
    # ----------------------------------------------------------------
    SYNTHETIC_GOAL_ID = None
    SYNTHETIC_USER_ID = None

    if not existing_goals:
        print("\n[Step 2] No real goals found. Inserting a synthetic test user + goal...")
        
        # We need to introspect Member 2's users table to seed safely
        from sqlalchemy import Table
        users_table = Table("users", investment_goals_table.metadata, autoload_with=engine)
        
        with engine.begin() as conn:
            # Insert a temp test user
            user_result = conn.execute(
                users_table.insert().values(
                    email="test_snapshot_user_delete_me@test.com",
                    hashed_password="not_real",
                ).returning(users_table.c.id)
            )
            SYNTHETIC_USER_ID = user_result.fetchone()[0]
            print(f"   ✅ Inserted synthetic user with ID: {SYNTHETIC_USER_ID}")

            # Now insert the goal under the real user
            goal_result = conn.execute(
                investment_goals_table.insert().values(
                    user_id=SYNTHETIC_USER_ID,
                    goal_name="Test Goal (Synthetic — Safe to Delete)",
                    target_amount=100000.0,
                    target_date=date(2028, 1, 1),
                    initial_capital=10000.0,
                    current_value=11500.0,
                    currency="USD"
                ).returning(investment_goals_table.c.id)
            )
            SYNTHETIC_GOAL_ID = goal_result.fetchone()[0]
        print(f"   ✅ Inserted synthetic goal with ID: {SYNTHETIC_GOAL_ID}")
    else:
        print("   ✅ Using existing real goals from the database.")

    # ----------------------------------------------------------------
    # STEP 3: Run the snapshot job
    # ----------------------------------------------------------------
    print("\n[Step 3] Running record_goal_snapshots() job...")
    from ingestion.goal_snapshotter import record_goal_snapshots
    record_goal_snapshots()

    # ----------------------------------------------------------------
    # STEP 4: Read back and display goal_snapshots table
    # ----------------------------------------------------------------
    print("\n[Step 4] Reading back goal_snapshots from NeonDB...")
    with Session(engine) as db:
        snapshots = db.query(GoalSnapshot).order_by(GoalSnapshot.snapshot_date.desc()).limit(10).all()

    if snapshots:
        print(f"\n✅ SUCCESS! {len(snapshots)} Snapshot(s) found in database:\n")
        print(f"{'GOAL_ID':<10} | {'DATE':<14} | {'PROJECTED VALUE'}")
        print("-" * 50)
        for s in snapshots:
            print(f"{s.goal_id:<10} | {str(s.snapshot_date):<14} | ${s.projected_value:,.2f}")
    else:
        print("⚠️ No snapshots found after running the job. Check logs above.")

    # ----------------------------------------------------------------
    # STEP 5: Clean up synthetic test data to keep DB pristine
    # ----------------------------------------------------------------
    if SYNTHETIC_GOAL_ID is not None:
        print(f"\n[Step 5] Cleaning up synthetic test goal (ID: {SYNTHETIC_GOAL_ID})...")
        with Session(engine) as db:
            db.query(GoalSnapshot).filter(GoalSnapshot.goal_id == SYNTHETIC_GOAL_ID).delete()
            db.commit()
        with engine.begin() as conn:
            conn.execute(investment_goals_table.delete().where(
                investment_goals_table.c.id == SYNTHETIC_GOAL_ID
            ))
        print("   ✅ Cleaned up synthetic goal.")

    if SYNTHETIC_USER_ID is not None:
        from sqlalchemy import Table, text
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": SYNTHETIC_USER_ID})
        print("   ✅ Cleaned up synthetic user.")

    print("\n" + "=" * 70)
    print("Task 13 Verification Complete.")
    print("=" * 70)

if __name__ == "__main__":
    verify_goal_snapshots()
