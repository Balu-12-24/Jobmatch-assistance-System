from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, check_premium_access
from app.models.user import User
from app.models.job import Job, SavedJob
from app.services.job_matcher import JobMatcher
from app.services.embedding_generator import get_embedding_generator
from app.services.salary_predictor import get_salary_predictor
from app.services.company_fit_analyzer import get_company_fit_analyzer
from app.schemas.job import JobRecommendationsResponse, JobMatchResponse, JobResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# Initialize services
job_matcher = JobMatcher()
embedding_gen = get_embedding_generator()
salary_predictor = get_salary_predictor()
company_fit_analyzer = get_company_fit_analyzer()


@router.get("/recommendations", response_model=JobRecommendationsResponse)
async def get_job_recommendations(
    top_k: int = Query(10, ge=1, le=50),
    location: Optional[str] = None,
    remote_option: Optional[str] = None,
    industry: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized job recommendations based on user's resume.
    
    - Requires user to have uploaded a resume
    - Returns top matching jobs with compatibility scores
    - Supports filtering by location, remote option, and industry
    """
    # Check if user has a profile with resume
    profile = current_user.profile
    if not profile or not profile.resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload your resume first to get job recommendations"
        )
    
    try:
        # Generate embedding for user's resume
        logger.info(f"Generating resume embedding for user {current_user.id}")
        resume_embedding = embedding_gen.generate_embedding(profile.resume_text)
        
        # Build user preferences from query params and profile
        user_preferences = {}
        if location:
            user_preferences['location'] = location
        elif profile.location:
            user_preferences['location'] = profile.location
            
        if remote_option:
            user_preferences['remote_option'] = remote_option
        elif profile.preferences and profile.preferences.get('remote_option'):
            user_preferences['remote_option'] = profile.preferences['remote_option']
            
        if industry:
            user_preferences['industry'] = industry
        elif profile.preferences and profile.preferences.get('industry'):
            user_preferences['industry'] = profile.preferences['industry']
        
        # Find matching jobs
        logger.info(f"Finding job matches for user {current_user.id}")
        job_matches = job_matcher.find_matches(
            resume_embedding=resume_embedding,
            user_preferences=user_preferences if user_preferences else None,
            top_k=top_k,
            db=db
        )
        
        # Enhance matches with skill gap analysis and salary prediction
        resume_skills = profile.skills or []
        enhanced_matches = []
        
        for match in job_matches:
            # Perform skill gap analysis
            skill_gap = job_matcher.identify_skill_gaps(
                resume_skills=resume_skills,
                job_requirements=match.job.requirements or ""
            )
            
            # Update match with skill analysis
            match.matching_skills = skill_gap.matching_skills
            match.missing_skills = skill_gap.missing_skills
            
            # Predict salary
            salary_prediction = None
            if salary_predictor.is_trained:
                try:
                    salary_prediction = salary_predictor.predict_salary(
                        experience_years=profile.experience_years or 2,
                        skill_count=len(resume_skills),
                        education_level=profile.education_level or 'bachelor',
                        location=match.job.location or 'San Francisco',
                        industry=match.job.industry or 'technology'
                    )
                    
                    # For free users, show only basic range
                    if not current_user.is_premium:
                        salary_prediction = {
                            "predicted_min": salary_prediction["predicted_min"],
                            "predicted_max": salary_prediction["predicted_max"],
                            "is_premium": False
                        }
                    else:
                        salary_prediction["is_premium"] = True
                        
                except Exception as e:
                    logger.error(f"Error predicting salary: {e}")
            
            # Calculate company fit score
            company_fit_score = None
            company_fit_explanation = None
            if profile.preferences:
                try:
                    fit_result = company_fit_analyzer.calculate_fit_score(
                        user_preferences=profile.preferences,
                        job_description=match.job.description,
                        company_size=match.job.company_size,
                        remote_option=match.job.remote_option,
                        industry=match.job.industry
                    )
                    
                    # For free users, show only basic score
                    if current_user.is_premium:
                        company_fit_score = fit_result.score
                        company_fit_explanation = fit_result.explanation
                    else:
                        company_fit_score = fit_result.score
                        company_fit_explanation = "Upgrade to premium for detailed insights"
                        
                except Exception as e:
                    logger.error(f"Error calculating company fit: {e}")
            
            # Convert to response model
            match_response = JobMatchResponse(
                job=JobResponse.from_orm(match.job),
                compatibility_score=match.compatibility_score,
                matching_skills=match.matching_skills,
                missing_skills=match.missing_skills,
                salary_prediction=salary_prediction,
                company_fit_score=company_fit_score,
                company_fit_explanation=company_fit_explanation
            )
            enhanced_matches.append(match_response)
        
        logger.info(f"Returning {len(enhanced_matches)} job recommendations")
        return JobRecommendationsResponse(
            matches=enhanced_matches,
            total_count=len(enhanced_matches)
        )
        
    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/save")
async def save_job(
    job_id: int,
    compatibility_score: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a job to user's saved jobs list"""
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already saved
    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id
    ).first()
    
    if existing:
        return {"message": "Job already saved", "saved_job_id": existing.id}
    
    # Save job
    saved_job = SavedJob(
        user_id=current_user.id,
        job_id=job_id,
        compatibility_score=int(compatibility_score) if compatibility_score else None
    )
    
    db.add(saved_job)
    db.commit()
    db.refresh(saved_job)
    
    logger.info(f"User {current_user.id} saved job {job_id}")
    return {"message": "Job saved successfully", "saved_job_id": saved_job.id}


@router.get("/saved", response_model=JobRecommendationsResponse)
async def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved jobs"""
    saved_jobs = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id
    ).all()
    
    matches = []
    for saved_job in saved_jobs:
        job = db.query(Job).filter(Job.id == saved_job.job_id).first()
        if job:
            match_response = JobMatchResponse(
                job=JobResponse.from_orm(job),
                compatibility_score=float(saved_job.compatibility_score) if saved_job.compatibility_score else 0.0,
                matching_skills=[],
                missing_skills=[]
            )
            matches.append(match_response)
    
    return JobRecommendationsResponse(
        matches=matches,
        total_count=len(matches)
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_details(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job
