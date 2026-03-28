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

class SimulationRequest(BaseModel):
    risk_level_override: Optional[int] = Field(None, ge=1, le=5, description="Test a different risk level.")
    capital_override: Optional[float] = Field(None, gt=0, description="Test adding or removing capital.")

class SimulationResponse(BaseModel):
    new_allocation: Dict[str, float]
    new_expected_return: float
    new_expected_volatility: float
    new_sharpe_ratio: float
    delta_return: Optional[float] = None
    delta_volatility: Optional[float] = None

class ChatMessage(BaseModel):
    message: str = Field(..., description="The user's chat message to the AI")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="The AI's text response")
    run_simulation: bool = Field(default=False, description="Flag for the frontend to trigger a What-If simulation overlay")
    suggested_overrides: Optional[Dict[str, float]] = Field(default=None, description="Parameters to pass to /simulate if run_simulation is true")
