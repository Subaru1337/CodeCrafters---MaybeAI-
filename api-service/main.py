from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

import models
from db import engine
from routers import auth_router, profile_router, portfolio_router, chat_router, research_router, insights_router, goals_router, watchlist_router, collab_router

# Create all database tables based on models.py
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Smart Finance Intelligence API",
    description="Backend API for portfolio optimization, what-if simulations, and financial intelligence (Member 2).",
    version="1.0.0"
)

# Hackathon wildcard CORS to prevent any React fetch issues
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(portfolio_router.router)
app.include_router(chat_router.router)
app.include_router(research_router.router)
app.include_router(insights_router.router)
app.include_router(goals_router.router)
app.include_router(watchlist_router.router)
app.include_router(collab_router.router)

@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "API is running"}

# Routers will be included here as we build them out
