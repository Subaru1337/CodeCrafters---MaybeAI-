from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import auth, models, schemas
from db import get_db

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("", status_code=201)
def add_to_watchlist(item: schemas.WatchlistCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Add a company to the user's watchlist."""
    exists = db.query(models.WatchlistItem).filter(
        models.WatchlistItem.user_id == current_user.id,
        models.WatchlistItem.company_id == item.company_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Company already in watchlist.")
    new_item = models.WatchlistItem(user_id=current_user.id, company_id=item.company_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("", response_model=List[schemas.WatchlistOut])
def get_watchlist(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get all watchlist items for the current user."""
    return db.query(models.WatchlistItem).filter(models.WatchlistItem.user_id == current_user.id).all()


@router.delete("/{company_id}", status_code=204)
def remove_from_watchlist(company_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Remove a company from the user's watchlist."""
    item = db.query(models.WatchlistItem).filter(
        models.WatchlistItem.user_id == current_user.id,
        models.WatchlistItem.company_id == company_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in watchlist.")
    db.delete(item)
    db.commit()
