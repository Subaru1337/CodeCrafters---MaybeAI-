from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

import auth, models, schemas
from db import get_db

router = APIRouter(prefix="/portfolio", tags=["Collaborative Portfolios"])


# ─────────────────────────────────────────────────────────────
# Task 14a: POST /portfolio/{id}/share
# Share a portfolio with another user by email
# ─────────────────────────────────────────────────────────────
@router.post("/{portfolio_id}/share", status_code=201)
def share_portfolio(
    portfolio_id: int,
    request: schemas.SharePortfolioRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Share your portfolio with another registered user by email.
    Permission: 'view' (read-only) or 'edit' (can comment + view).
    """
    # Verify portfolio ownership
    portfolio = db.query(models.SavedPortfolio).filter(
        models.SavedPortfolio.id == portfolio_id,
        models.SavedPortfolio.user_id == current_user.id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or you do not own it.")

    # Find collaborator by email
    collaborator = db.query(models.User).filter(
        models.User.email == request.collaborator_email
    ).first()
    if not collaborator:
        raise HTTPException(status_code=404, detail=f"No user found with email '{request.collaborator_email}'.")

    if collaborator.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot share a portfolio with yourself.")

    # Check for duplicate share
    existing = db.query(models.PortfolioCollaborator).filter(
        models.PortfolioCollaborator.portfolio_id == portfolio_id,
        models.PortfolioCollaborator.collaborator_user_id == collaborator.id
    ).first()
    if existing:
        # Update permission if already shared
        existing.permission = request.permission
        db.commit()
        db.refresh(existing)
        return {
            "message": f"Updated permission for {request.collaborator_email} to '{request.permission}'.",
            "collaborator_id": existing.id
        }

    # Create new collaborator record
    new_collab = models.PortfolioCollaborator(
        portfolio_id=portfolio_id,
        owner_user_id=current_user.id,
        collaborator_user_id=collaborator.id,
        permission=request.permission
    )
    db.add(new_collab)
    db.commit()
    db.refresh(new_collab)

    return {
        "message": f"Portfolio shared with {request.collaborator_email} ({request.permission} access).",
        "collaborator_id": new_collab.id
    }


# ─────────────────────────────────────────────────────────────
# Task 14b: GET /portfolio/shared-with-me
# List portfolios others have shared with the current user
# ─────────────────────────────────────────────────────────────
@router.get("/shared-with-me")
def get_shared_with_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Returns all portfolios that other users have shared with you.
    Includes the portfolio allocation, metrics, owner email, and your permission level.
    """
    collabs = db.query(models.PortfolioCollaborator).filter(
        models.PortfolioCollaborator.collaborator_user_id == current_user.id
    ).all()

    result = []
    for collab in collabs:
        portfolio = db.query(models.SavedPortfolio).filter(
            models.SavedPortfolio.id == collab.portfolio_id
        ).first()
        owner = db.query(models.User).filter(
            models.User.id == collab.owner_user_id
        ).first()
        if portfolio and owner:
            result.append({
                "collaboration_id": collab.id,
                "permission": collab.permission,
                "invited_at": collab.invited_at,
                "shared_by": owner.email,
                "portfolio": {
                    "id": portfolio.id,
                    "allocation": portfolio.allocation,
                    "expected_return": portfolio.expected_return,
                    "expected_volatility": portfolio.expected_volatility,
                    "sharpe_ratio": portfolio.sharpe_ratio,
                    "reasoning": portfolio.reasoning,
                    "created_at": portfolio.created_at,
                }
            })

    return {"shared_portfolios": result, "count": len(result)}


# ─────────────────────────────────────────────────────────────
# Task 14c: POST /portfolio/{id}/comments
# Add a comment to a portfolio (owner or collaborator)
# ─────────────────────────────────────────────────────────────
@router.post("/{portfolio_id}/comments", status_code=201)
def add_comment(
    portfolio_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Post a comment on a portfolio.
    Allowed for: the portfolio owner, or any collaborator with view/edit access.
    """
    portfolio = db.query(models.SavedPortfolio).filter(
        models.SavedPortfolio.id == portfolio_id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")

    # Access check: must be owner OR a collaborator
    is_owner = portfolio.user_id == current_user.id
    is_collaborator = db.query(models.PortfolioCollaborator).filter(
        models.PortfolioCollaborator.portfolio_id == portfolio_id,
        models.PortfolioCollaborator.collaborator_user_id == current_user.id
    ).first()

    if not is_owner and not is_collaborator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to comment on this portfolio."
        )

    new_comment = models.PortfolioComment(
        portfolio_id=portfolio_id,
        user_id=current_user.id,
        comment_text=comment.comment_text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "id": new_comment.id,
        "portfolio_id": new_comment.portfolio_id,
        "user_id": new_comment.user_id,
        "commenter_email": current_user.email,
        "comment_text": new_comment.comment_text,
        "created_at": new_comment.created_at
    }


# ─────────────────────────────────────────────────────────────
# Task 14d: GET /portfolio/{id}/comments
# Get all comments on a portfolio
# ─────────────────────────────────────────────────────────────
@router.get("/{portfolio_id}/comments")
def get_comments(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get all comments on a portfolio.
    Returns commenter email, text, and timestamp.
    Access: portfolio owner or any collaborator.
    """
    portfolio = db.query(models.SavedPortfolio).filter(
        models.SavedPortfolio.id == portfolio_id
    ).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found.")

    is_owner = portfolio.user_id == current_user.id
    is_collaborator = db.query(models.PortfolioCollaborator).filter(
        models.PortfolioCollaborator.portfolio_id == portfolio_id,
        models.PortfolioCollaborator.collaborator_user_id == current_user.id
    ).first()

    if not is_owner and not is_collaborator:
        raise HTTPException(status_code=403, detail="Access denied.")

    comments = db.query(models.PortfolioComment).filter(
        models.PortfolioComment.portfolio_id == portfolio_id
    ).order_by(models.PortfolioComment.created_at).all()

    result = []
    for c in comments:
        commenter = db.query(models.User).filter(models.User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "portfolio_id": c.portfolio_id,
            "user_id": c.user_id,
            "commenter_email": commenter.email if commenter else "unknown",
            "comment_text": c.comment_text,
            "created_at": c.created_at
        })

    return {"comments": result, "count": len(result)}


# ─────────────────────────────────────────────────────────────
# BONUS: DELETE /portfolio/{id}/share/{collaborator_id}
# Revoke portfolio access
# ─────────────────────────────────────────────────────────────
@router.delete("/{portfolio_id}/share/{collaborator_id}", status_code=204)
def revoke_share(
    portfolio_id: int,
    collaborator_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Revoke a collaborator's access to your portfolio."""
    collab = db.query(models.PortfolioCollaborator).filter(
        models.PortfolioCollaborator.id == collaborator_id,
        models.PortfolioCollaborator.portfolio_id == portfolio_id,
        models.PortfolioCollaborator.owner_user_id == current_user.id
    ).first()
    if not collab:
        raise HTTPException(status_code=404, detail="Share record not found.")
    db.delete(collab)
    db.commit()
