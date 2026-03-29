from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from db import get_db
import models, schemas, auth

router = APIRouter(
    prefix="/profile",
    tags=["Investor Profile"]
)

@router.post("", response_model=schemas.ProfileOut)
def create_profile(
    profile: schemas.ProfileCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new investor profile for the currently authenticated user."""
    # Check if a profile already exists for this user
    if current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already has an investor profile. Use PUT to update."
        )
    
    # Create the new profile
    db_profile = models.InvestorProfile(
        **profile.model_dump(),
        user_id=current_user.id
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("", response_model=schemas.ProfileOut)
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    """Fetch the authenticated user's investor profile."""
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Investor profile not found. Please create one first."
        )
    return current_user.profile

@router.put("", response_model=schemas.ProfileOut)
def update_profile(
    profile_update: schemas.ProfileCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """Update an existing investor profile."""
    db_profile = current_user.profile
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Investor profile not found. Please create one first."
        )
    
    # Update properties
    update_data = profile_update.model_dump()
    for key, value in update_data.items():
        setattr(db_profile, key, value)
        
    db_profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_profile)
    return db_profile
