from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("InvestorProfile", back_populates="user", uselist=False)
    portfolios = relationship("SavedPortfolio", back_populates="user")
    watchlist = relationship("WatchlistItem", back_populates="user")
    goals = relationship("InvestmentGoal", back_populates="user")
    goal_snapshots = relationship("GoalSnapshot", back_populates="user")


class InvestorProfile(Base):
    __tablename__ = "investor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    risk_level = Column(Integer, nullable=False) # 1-5
    capital_amount = Column(Float, nullable=False)
    time_horizon_years = Column(Integer, nullable=False)
    tax_bracket = Column(String, nullable=True)
    investor_type = Column(String, nullable=True)
    regulatory_constraints = Column(JSON, nullable=True) # JSON list
    target_return_pct = Column(Float, nullable=True)
    preferred_language = Column(String, default='English')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
    portfolios = relationship("SavedPortfolio", back_populates="profile")


class SavedPortfolio(Base):
    __tablename__ = "saved_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("investor_profiles.id"), nullable=False)
    allocation = Column(JSON, nullable=False) # {'AAPL': 20.0, 'MSFT': 30.0, etc.}
    expected_return = Column(Float, nullable=False)
    expected_volatility = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="portfolios")
    profile = relationship("InvestorProfile", back_populates="portfolios")
    collaborators = relationship("PortfolioCollaborator", back_populates="portfolio")
    comments = relationship("PortfolioComment", back_populates="portfolio")


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, nullable=False) # Foreign key to Member 1's companies table
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="watchlist")


class InvestmentGoal(Base):
    __tablename__ = "investment_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    target_date = Column(Date, nullable=False)
    initial_capital = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="goals")
    snapshots = relationship("GoalSnapshot", back_populates="goal", cascade="all, delete-orphan")


class GoalSnapshot(Base):
    """Tracks a point-in-time snapshot of a goal's current_value for progress history."""
    __tablename__ = "goal_snapshots_api"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("investment_goals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_value = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    goal = relationship("InvestmentGoal", back_populates="snapshots")
    user = relationship("User", back_populates="goal_snapshots")


class PortfolioCollaborator(Base):
    __tablename__ = "portfolio_collaborators"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("saved_portfolios.id"), nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    collaborator_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission = Column(String, nullable=False) # 'view' or 'edit'
    invited_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("SavedPortfolio", back_populates="collaborators")
    owner = relationship("User", foreign_keys=[owner_user_id])
    collaborator = relationship("User", foreign_keys=[collaborator_user_id])


class PortfolioComment(Base):
    __tablename__ = "portfolio_comments"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("saved_portfolios.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("SavedPortfolio", back_populates="comments")
    user = relationship("User")
