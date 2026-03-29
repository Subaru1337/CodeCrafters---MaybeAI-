import sys
import os

# Absolute path resolution — works regardless of CWD when uvicorn starts
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
_API_ROOT  = os.path.dirname(_THIS_DIR)
_DATA_ROOT = os.path.join(os.path.dirname(_API_ROOT), "data-service")

if _DATA_ROOT not in sys.path:
    sys.path.insert(0, _DATA_ROOT)

from fastapi import APIRouter, Depends, HTTPException
import auth
import models
from ai.service import get_bias_report

router = APIRouter(
    prefix="/insights",
    tags=["Insights & Behavioral Analysis"]
)

# ─────────────────────────────────────────────────────────────
# INT-7: GET /insights/biases
# ─────────────────────────────────────────────────────────────

@router.get("/biases")
def get_behavioral_biases(
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Analyzes the current user's latest saved portfolio against AI sentiment scores.
    Returns a list of detected behavioral biases:
    - Under-Diversification Bias
    - Confirmation Bias Risk (heavy allocation into bearish stocks)
    - Herd/FOMO Risk (heavy concentration in overbought stocks)
    """
    result = get_bias_report(current_user.id)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "user_id": current_user.id,
        "is_biased": result.get("is_biased", False),
        "bias_warnings": result.get("bias_warnings", []),
        "message": result.get("message", None)
    }
