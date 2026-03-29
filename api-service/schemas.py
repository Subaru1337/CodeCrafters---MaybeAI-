from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional, Dict

# ── Goals ──────────────────────────────────────────
class GoalCreate(BaseModel):
    goal_name: str
    target_amount: float
    target_date: date
    initial_capital: float
    current_value: float
    currency: str = "USD"

class GoalOut(GoalCreate):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class GoalSnapshotCreate(BaseModel):
    current_value: float
    note: Optional[str] = None

class GoalSnapshotOut(BaseModel):
    id: int
    goal_id: int
    current_value: float
    note: Optional[str] = None
    recorded_at: datetime
    class Config:
        from_attributes = True

# ── Watchlist ───────────────────────────────────────
class WatchlistCreate(BaseModel):
    company_id: int

class WatchlistOut(BaseModel):
    id: int
    user_id: int
    company_id: int
    added_at: datetime
    class Config:
        from_attributes = True


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

# ── Collaborative Portfolios ────────────────────────────────
class SharePortfolioRequest(BaseModel):
    collaborator_email: str
    permission: str = Field(default="view", pattern="^(view|edit)$")

class CollaboratorOut(BaseModel):
    id: int
    portfolio_id: int
    collaborator_email: str
    permission: str
    invited_at: datetime
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    comment_text: str = Field(..., min_length=1)

class CommentOut(BaseModel):
    id: int
    portfolio_id: int
    user_id: int
    commenter_email: str
    comment_text: str
    created_at: datetime
    class Config:
        from_attributes = True
