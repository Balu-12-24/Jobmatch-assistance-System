from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserProfileResponse, UserProfileUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information.
    
    Returns user details and profile data including skills, experience, and preferences.
    """
    profile = current_user.profile
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_premium": current_user.is_premium,
            "created_at": current_user.created_at
        },
        "profile": {
            "skills": profile.skills or [],
            "experience_years": profile.experience_years,
            "education_level": profile.education_level,
            "location": profile.location,
            "preferences": profile.preferences or {},
            "has_resume": bool(profile.resume_text),
            "updated_at": profile.updated_at
        }
    }


@router.put("", response_model=dict)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile preferences.
    
    Allows updating:
    - Location
    - Preferences (remote_option, company_size, industry, work_culture)
    """
    profile = current_user.profile
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update location if provided
    if profile_update.location is not None:
        profile.location = profile_update.location
    
    # Update preferences if provided
    if profile_update.preferences is not None:
        # Merge with existing preferences
        current_prefs = profile.preferences or {}
        current_prefs.update(profile_update.preferences)
        profile.preferences = current_prefs
    
    try:
        db.commit()
        db.refresh(profile)
        logger.info(f"Profile updated for user {current_user.id}")
        
        return {
            "message": "Profile updated successfully",
            "profile": {
                "skills": profile.skills or [],
                "experience_years": profile.experience_years,
                "education_level": profile.education_level,
                "location": profile.location,
                "preferences": profile.preferences or {},
                "updated_at": profile.updated_at
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )
