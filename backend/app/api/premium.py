from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/premium", tags=["Premium"])


@router.post("/upgrade")
async def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user to premium tier.
    
    For hackathon: Simply sets is_premium flag to True.
    In production: Would integrate with Stripe for payment processing.
    """
    if current_user.is_premium:
        return {
            "message": "User is already premium",
            "is_premium": True
        }
    
    try:
        # TODO: In production, integrate with Stripe:
        # 1. Create Stripe checkout session
        # 2. Verify payment
        # 3. Create subscription
        # 4. Set is_premium flag
        
        # For hackathon: Just set the flag
        current_user.is_premium = True
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User {current_user.id} upgraded to premium")
        
        return {
            "message": "Successfully upgraded to premium!",
            "is_premium": True,
            "features_unlocked": [
                "Detailed salary predictions with percentiles",
                "Company-fit score explanations",
                "Skill gap recommendations",
                "Unlimited job searches",
                "Priority support"
            ]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error upgrading user to premium: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing premium upgrade"
        )


@router.get("/features")
async def get_premium_features():
    """
    Get list of premium features and pricing.
    Public endpoint - no authentication required.
    """
    return {
        "pricing": {
            "monthly": 9.99,
            "currency": "USD"
        },
        "features": {
            "free": [
                "Basic job matching",
                "Top 10 job recommendations",
                "Compatibility scores",
                "Basic salary ranges",
                "Basic company-fit scores"
            ],
            "premium": [
                "Unlimited job searches",
                "Detailed salary predictions",
                "Salary percentiles and confidence intervals",
                "Company-fit score explanations",
                "Detailed skill gap analysis",
                "Skill development recommendations",
                "Resume optimization suggestions",
                "Priority support",
                "Early access to new features"
            ]
        },
        "trial": {
            "available": True,
            "duration_days": 7,
            "description": "Try premium features free for 7 days"
        }
    }


@router.get("/status")
async def get_premium_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's premium status.
    """
    return {
        "is_premium": current_user.is_premium,
        "user_id": current_user.id,
        "email": current_user.email
    }
