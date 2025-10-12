"""
Salary Prediction API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, check_premium_access
from app.models.user import User
from app.services.salary_predictor import get_salary_predictor
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/salary", tags=["Salary Prediction"])


class SalaryPredictionRequest(BaseModel):
    """Request for salary prediction"""
    experience_years: int = Field(..., ge=0, le=50, description="Years of experience")
    skill_count: int = Field(..., ge=0, le=50, description="Number of skills")
    education_level: str = Field(..., description="Education level (B.Tech, MBA, M.Tech, etc.)")
    location: str = Field(..., description="Job location")
    industry: str = Field(..., description="Industry sector")
    city_tier: Optional[int] = Field(1, ge=1, le=3, description="City tier (1, 2, 3)")
    company_type: Optional[str] = Field("service", description="Company type (MNC, startup, service, product, BPO, KPO)")
    education_institution: Optional[str] = Field("Tier 2", description="Education institution (IIT, NIT, IIM, BITS, etc.)")


class SalaryPredictionResponse(BaseModel):
    """Response with salary prediction"""
    predicted_min: int
    predicted_max: int
    predicted_mean: int
    confidence: float
    percentile_25: Optional[int] = None
    percentile_75: Optional[int] = None
    # Indian format fields
    salary_lpa: Optional[float] = None
    salary_lpa_formatted: Optional[str] = None
    monthly_ctc: Optional[int] = None
    monthly_ctc_formatted: Optional[str] = None
    annual_inr: Optional[int] = None
    annual_inr_formatted: Optional[str] = None
    is_premium: bool


@router.post("/predict", response_model=SalaryPredictionResponse)
async def predict_salary(
    request: SalaryPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict salary based on user profile and job characteristics.
    
    Provides salary prediction with:
    - Predicted salary range (min, max, mean)
    - Confidence score
    - Percentile ranges (25th, 75th)
    - Indian formats (LPA, monthly CTC) for Indian jobs
    
    Free tier: Basic salary range
    Premium tier: Detailed breakdown with percentiles and city/company-wise variations
    
    Args:
        request: Salary prediction parameters
    
    Returns:
        SalaryPredictionResponse: Predicted salary with confidence
    
    Requires:
        Valid JWT token
    """
    try:
        logger.info(f"Predicting salary for user {current_user.id}")
        
        # Get salary predictor
        predictor = get_salary_predictor()
        
        # Make prediction
        prediction = predictor.predict_salary(
            experience_years=request.experience_years,
            skill_count=request.skill_count,
            education_level=request.education_level,
            location=request.location,
            industry=request.industry,
            city_tier=request.city_tier or 1,
            company_type=request.company_type or "service",
            education_institution=request.education_institution or "Tier 2"
        )
        
        # Check if user is premium
        is_premium = current_user.is_premium
        
        # For free users, limit detailed information
        if not is_premium:
            prediction.pop("percentile_25", None)
            prediction.pop("percentile_75", None)
        
        prediction["is_premium"] = is_premium
        
        return SalaryPredictionResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error predicting salary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting salary: {str(e)}"
        )


@router.post("/predict/premium", response_model=SalaryPredictionResponse)
async def predict_salary_premium(
    request: SalaryPredictionRequest,
    current_user: User = Depends(check_premium_access),
    db: Session = Depends(get_db)
):
    """
    Premium salary prediction with detailed breakdown.
    
    Premium features include:
    - Detailed percentile ranges (25th, 75th)
    - City-wise salary variations
    - Company-type-wise breakdown
    - Confidence intervals
    - Historical trends
    
    Args:
        request: Salary prediction parameters
    
    Returns:
        SalaryPredictionResponse: Complete salary prediction with all details
    
    Requires:
        - Valid JWT token
        - Premium subscription
    """
    try:
        logger.info(f"Premium salary prediction for user {current_user.id}")
        
        # Get salary predictor
        predictor = get_salary_predictor()
        
        # Make prediction with all details
        prediction = predictor.predict_salary(
            experience_years=request.experience_years,
            skill_count=request.skill_count,
            education_level=request.education_level,
            location=request.location,
            industry=request.industry,
            city_tier=request.city_tier or 1,
            company_type=request.company_type or "service",
            education_institution=request.education_institution or "Tier 2"
        )
        
        prediction["is_premium"] = True
        
        return SalaryPredictionResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error in premium salary prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting salary: {str(e)}"
        )


@router.get("/predict/profile", response_model=SalaryPredictionResponse)
async def predict_salary_from_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict salary based on user's profile data.
    
    Uses the user's uploaded resume and profile information to predict
    expected salary range.
    
    Returns:
        SalaryPredictionResponse: Predicted salary based on profile
    
    Requires:
        - Valid JWT token
        - User must have completed profile with resume
    """
    profile = current_user.profile
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile first."
        )
    
    if not profile.skills or not profile.experience_years:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete profile. Please upload a resume or add experience and skills."
        )
    
    try:
        logger.info(f"Predicting salary from profile for user {current_user.id}")
        
        # Get salary predictor
        predictor = get_salary_predictor()
        
        # Extract profile data
        skill_count = len(profile.skills) if profile.skills else 0
        experience_years = profile.experience_years or 0
        education_level = profile.education_level or "B.Tech"
        location = profile.location or "Bangalore"
        education_institution = profile.education_institution or "Tier 2"
        
        # Infer industry from skills (simple heuristic)
        industry = "IT"  # Default
        if profile.skills:
            skills_lower = [s.lower() for s in profile.skills]
            if any(s in skills_lower for s in ["finance", "accounting", "audit"]):
                industry = "Finance"
            elif any(s in skills_lower for s in ["medical", "healthcare", "nursing"]):
                industry = "Healthcare"
        
        # Make prediction
        prediction = predictor.predict_salary(
            experience_years=experience_years,
            skill_count=skill_count,
            education_level=education_level,
            location=location,
            industry=industry,
            city_tier=1,  # Default to Tier 1
            company_type="service",  # Default
            education_institution=education_institution
        )
        
        # Check if user is premium
        is_premium = current_user.is_premium
        
        if not is_premium:
            prediction.pop("percentile_25", None)
            prediction.pop("percentile_75", None)
        
        prediction["is_premium"] = is_premium
        
        return SalaryPredictionResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Error predicting salary from profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting salary: {str(e)}"
        )
