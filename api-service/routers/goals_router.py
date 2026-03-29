from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

import auth, models, schemas
from db import get_db

router = APIRouter(prefix="/goals", tags=["Investment Goals"])


# ─────────────────────────────────────────────────────────────
# Task 12a: POST /goals — Create a new investment goal
# ─────────────────────────────────────────────────────────────
@router.post("", status_code=201, response_model=schemas.GoalOut)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new investment goal for the current user."""
    new_goal = models.InvestmentGoal(
        user_id=current_user.id,
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
        initial_capital=goal.initial_capital,
        current_value=goal.current_value,
        currency=goal.currency,
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    # Auto-record first snapshot on creation
    snapshot = models.GoalSnapshot(
        goal_id=new_goal.id,
        user_id=current_user.id,
        current_value=new_goal.current_value,
        note="Goal created"
    )
    db.add(snapshot)
    db.commit()
    return new_goal


# ─────────────────────────────────────────────────────────────
# Task 12b: GET /goals — List all goals for current user
# ─────────────────────────────────────────────────────────────
@router.get("", response_model=List[schemas.GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all investment goals for the current user."""
    return db.query(models.InvestmentGoal)\
             .filter(models.InvestmentGoal.user_id == current_user.id)\
             .order_by(desc(models.InvestmentGoal.created_at))\
             .all()


# ─────────────────────────────────────────────────────────────
# Task 12c: PUT /goals/{id} — Update a goal
# ─────────────────────────────────────────────────────────────
@router.put("/{goal_id}", response_model=schemas.GoalOut)
def update_goal(
    goal_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update an existing investment goal. Auto-snapshots current_value if it changed."""
    db_goal = db.query(models.InvestmentGoal).filter(
        models.InvestmentGoal.id == goal_id,
        models.InvestmentGoal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    old_value = db_goal.current_value
    db_goal.goal_name = goal.goal_name
    db_goal.target_amount = goal.target_amount
    db_goal.target_date = goal.target_date
    db_goal.initial_capital = goal.initial_capital
    db_goal.current_value = goal.current_value
    db_goal.currency = goal.currency
    db.commit()
    db.refresh(db_goal)

    # If current_value changed, auto-record a progress snapshot
    if goal.current_value != old_value:
        snapshot = models.GoalSnapshot(
            goal_id=goal_id,
            user_id=current_user.id,
            current_value=goal.current_value,
            note="Value updated"
        )
        db.add(snapshot)
        db.commit()

    return db_goal


# ─────────────────────────────────────────────────────────────
# Task 12d: DELETE /goals/{id} — Delete a goal
# ─────────────────────────────────────────────────────────────
@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete an investment goal and all its history snapshots."""
    db_goal = db.query(models.InvestmentGoal).filter(
        models.InvestmentGoal.id == goal_id,
        models.InvestmentGoal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    db.delete(db_goal)
    db.commit()


# ─────────────────────────────────────────────────────────────
# Task 12e: GET /goals/{id}/history — Goal progress history
# ─────────────────────────────────────────────────────────────
@router.get("/{goal_id}/history", response_model=List[schemas.GoalSnapshotOut])
def get_goal_history(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get the full progress history for a specific goal.
    Returns chronological snapshots of current_value over time.
    """
    # Verify ownership
    db_goal = db.query(models.InvestmentGoal).filter(
        models.InvestmentGoal.id == goal_id,
        models.InvestmentGoal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    snapshots = db.query(models.GoalSnapshot)\
                  .filter(models.GoalSnapshot.goal_id == goal_id)\
                  .order_by(models.GoalSnapshot.recorded_at)\
                  .all()
    return snapshots


# ─────────────────────────────────────────────────────────────
# BONUS: POST /goals/{id}/history — Manually record a snapshot
# ─────────────────────────────────────────────────────────────
@router.post("/{goal_id}/history", response_model=schemas.GoalSnapshotOut, status_code=201)
def record_goal_snapshot(
    goal_id: int,
    snapshot: schemas.GoalSnapshotCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Manually record a progress snapshot for a goal.
    Use this to log monthly contributions or value updates.
    Also updates the goal's current_value to the latest snapshot.
    """
    db_goal = db.query(models.InvestmentGoal).filter(
        models.InvestmentGoal.id == goal_id,
        models.InvestmentGoal.user_id == current_user.id
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    new_snapshot = models.GoalSnapshot(
        goal_id=goal_id,
        user_id=current_user.id,
        current_value=snapshot.current_value,
        note=snapshot.note
    )
    # Keep goal's current_value in sync
    db_goal.current_value = snapshot.current_value
    db.add(new_snapshot)
    db.commit()
    db.refresh(new_snapshot)
    return new_snapshot
