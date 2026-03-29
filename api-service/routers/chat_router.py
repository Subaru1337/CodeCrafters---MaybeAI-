from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
import json

from db import get_db
import models, schemas, auth

router = APIRouter(
    prefix="/chat",
    tags=["AI Assistant"]
)

# Initialize Gemini Client (Make sure GEMINI_API_KEY is in your .env)
from google import genai
from google.genai import types
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

@router.post("", response_model=schemas.ChatResponse)
def chat_with_assistant(
    chat_request: schemas.ChatMessage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Receives user chat messages, grabs their portfolio/profile context natively from the DB,
    and returns an AI response using Gemini. It intelligently returns a JSON parsing
    flag telling the frontend to execute the scenario engine if needed!
    """
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=400, detail="Profile required to provide personalized AI advice.")
        
    # 1. Gather User Context for the LLM
    latest_portfolio = db.query(models.SavedPortfolio)\
                         .filter(models.SavedPortfolio.user_id == current_user.id)\
                         .order_by(desc(models.SavedPortfolio.created_at))\
                         .first()
                         
    context_str = f"User Risk Level: {profile.risk_level}. "
    if latest_portfolio:
        context_str += f"Current Expected Portfolio Return: {latest_portfolio.expected_return*100:.2f}%. "

    # 2. Real LLM Call using Gemini
    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing from .env. Cannot contact LLM.")

    system_prompt = f"""You are a Smart Financial Assistant. 
The user's current context is: {context_str}
Your job is to reply to the user in a friendly, professional tone. 
CRITICAL GUARDRAIL: You are STRICTLY a financial and portfolio intelligence assistant. If the user asks ANY question unrelated to finance, investing, portfolios, or economics (e.g., "how to make an egg", general knowledge, coding help), you MUST politely refuse to answer, provide no information on the topic, and remind them of your financial purpose.
ALSO, detect if the user wants to run a "what-if" scenario, simulation, or wants to see what happens if they change their risk or capital.
You MUST respond ONLY with a valid JSON object in this exact format:
{{
    "reply": "Your natural language conversational response here",
    "run_simulation": true or false,
    "suggested_overrides": {{ "risk_level_override": integer between 1 and 5 }} (or null if no simulation needed)
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=chat_request.message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON coming back from the LLM
        ai_data = json.loads(response.text)
        
        return schemas.ChatResponse(
            reply=ai_data.get("reply", "I couldn't process that."),
            run_simulation=ai_data.get("run_simulation", False),
            suggested_overrides=ai_data.get("suggested_overrides")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
