from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class PortfolioOut(BaseModel):
    id: int
    user_id: int
    profile_id: int
    allocation: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    reasoning: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    risk_level: int = Field(ge=1, le=5, description="Risk tolerance level from 1 (lowest) to 5 (highest)")
    capital_amount: float = Field(gt=0, description="Total capital available for investment")
    time_horizon_years: int = Field(gt=0, description="Investment time horizon in years")
    tax_bracket: Optional[str] = None
    investor_type: Optional[str] = None
    regulatory_constraints: Optional[List[str]] = []
    target_return_pct: Optional[float] = None
    preferred_language: str = 'English'

class ProfileCreate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
