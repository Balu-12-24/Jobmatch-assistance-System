from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.resume_parser import ResumeParser
from app.services.resume_analyzer import ResumeAnalyzer
from app.schemas.resume import ResumeUploadResponse, ResumeAnalysisResponse, JobComparisonRequest, JobComparisonResponse
from app.core.dependencies import check_premium_access
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

# Initialize services
resume_parser = ResumeParser()
resume_analyzer = ResumeAnalyzer()

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a resume file (PDF or DOCX).
    
    - Validates file type and size
    - Extracts text and skills
    - Updates user profile
    - Returns parsed resume data
    """
    # Validate file extension
    file_ext = None
    if file.filename:
        file_ext = "." + file.filename.split(".")[-1].lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Parse resume
        logger.info(f"Parsing resume for user {current_user.id}: {file.filename}")
        parsed_resume = resume_parser.parse_file(content, file_ext)
        
        # Update user profile with parsed data
        profile = current_user.profile
        if profile:
            profile.resume_text = parsed_resume.raw_text
            profile.skills = parsed_resume.skills
            profile.experience_years = parsed_resume.experience_years
            profile.education_level = parsed_resume.education_level
            
            db.commit()
            db.refresh(profile)
            
            logger.info(f"Resume processed successfully for user {current_user.id}")
            
            return ResumeUploadResponse(
                message="Resume uploaded and processed successfully",
                skills=parsed_resume.skills,
                experience_years=parsed_resume.experience_years,
                education_level=parsed_resume.education_level,
                raw_text_preview=parsed_resume.raw_text[:200] + "..." if len(parsed_resume.raw_text) > 200 else parsed_resume.raw_text
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )



@router.get("/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive resume analysis with ATS score.
    
    Analyzes the user's uploaded resume and provides:
    - ATS compatibility score (0-100%) with breakdown
    - Strong sections identification
    - Weak sections with improvement suggestions
    - Unnecessary content to remove
    - Actionable improvement recommendations
    
    Returns:
        ResumeAnalysisResponse: Complete resume analysis
    
    Requires:
        - Valid JWT token
        - User must have uploaded a resume
    """
    profile = current_user.profile
    
    if not profile or not profile.resume_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )
    
    try:
        # Prepare parsed resume data
        parsed_resume = {
            "skills": profile.skills or [],
            "experience": [],  # Would be populated from parsed data
            "education": [],   # Would be populated from parsed data
            "experience_years": profile.experience_years or 0,
            "education_level": profile.education_level or ""
        }
        
        # Perform analysis
        logger.info(f"Analyzing resume for user {current_user.id}")
        analysis = resume_analyzer.analyze_resume(profile.resume_text, parsed_resume)
        
        # Check if user is premium for detailed features
        is_premium = current_user.is_premium
        
        # For free users, limit some features
        if not is_premium:
            # Show preview of premium features
            if len(analysis["improvement_suggestions"]) > 5:
                analysis["improvement_suggestions"] = analysis["improvement_suggestions"][:5]
                analysis["improvement_suggestions"].append("🔒 Upgrade to Premium for more detailed suggestions")
            
            if len(analysis["unnecessary_content"]) > 3:
                analysis["unnecessary_content"] = analysis["unnecessary_content"][:3]
                analysis["unnecessary_content"].append("🔒 Upgrade to Premium for complete analysis")
        
        return ResumeAnalysisResponse(
            ats_score=analysis["ats_score"],
            strong_sections=analysis["strong_sections"],
            weak_sections=analysis["weak_sections"],
            unnecessary_content=analysis["unnecessary_content"],
            improvement_suggestions=analysis["improvement_suggestions"],
            is_premium=is_premium
        )
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )


@router.post("/analyze-job", response_model=JobComparisonResponse)
async def analyze_resume_against_job(
    request: JobComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare resume with a specific job description to identify keyword gaps.
    
    Analyzes how well the user's resume matches a target job description:
    - Identifies matching keywords
    - Lists missing critical keywords
    - Calculates keyword match percentage
    - Provides tailored suggestions to improve match
    
    Args:
        request: Job description to compare against
    
    Returns:
        JobComparisonResponse: Keyword gap analysis and suggestions
    
    Requires:
        - Valid JWT token
        - User must have uploaded a resume
    """
    profile = current_user.profile
    
    if not profile or not profile.resume_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )
    
    if not request.job_description or len(request.job_description) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is too short or empty"
        )
    
    try:
        logger.info(f"Comparing resume with job description for user {current_user.id}")
        
        # Perform job-specific analysis
        comparison = resume_analyzer.compare_with_job(
            profile.resume_text,
            request.job_description
        )
        
        # Check if user is premium
        is_premium = current_user.is_premium
        
        # For free users, limit results
        if not is_premium:
            if len(comparison["matching_keywords"]) > 10:
                comparison["matching_keywords"] = comparison["matching_keywords"][:10]
            
            if len(comparison["missing_keywords"]) > 5:
                comparison["missing_keywords"] = comparison["missing_keywords"][:5]
                comparison["missing_keywords"].append("🔒 Upgrade to Premium for complete keyword analysis")
        
        return JobComparisonResponse(
            matching_keywords=comparison["matching_keywords"],
            missing_keywords=comparison["missing_keywords"],
            keyword_match_percentage=comparison["keyword_match_percentage"],
            suggestions=comparison["suggestions"],
            is_premium=is_premium
        )
        
    except Exception as e:
        logger.error(f"Error comparing resume with job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing job match: {str(e)}"
        )


@router.get("/analysis/premium", response_model=ResumeAnalysisResponse)
async def get_premium_resume_analysis(
    current_user: User = Depends(check_premium_access),
    db: Session = Depends(get_db)
):
    """
    Get detailed premium resume analysis with full insights.
    
    Premium features include:
    - Complete improvement suggestions (unlimited)
    - Detailed keyword density analysis
    - Line-by-line feedback
    - Industry-specific recommendations
    - Complete unnecessary content list
    
    Returns:
        ResumeAnalysisResponse: Complete premium resume analysis
    
    Requires:
        - Valid JWT token
        - Premium subscription
        - User must have uploaded a resume
    """
    profile = current_user.profile
    
    if not profile or not profile.resume_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )
    
    try:
        # Prepare parsed resume data
        parsed_resume = {
            "skills": profile.skills or [],
            "experience": [],
            "education": [],
            "experience_years": profile.experience_years or 0,
            "education_level": profile.education_level or ""
        }
        
        # Perform full analysis (no limitations)
        logger.info(f"Performing premium analysis for user {current_user.id}")
        analysis = resume_analyzer.analyze_resume(profile.resume_text, parsed_resume)
        
        return ResumeAnalysisResponse(
            ats_score=analysis["ats_score"],
            strong_sections=analysis["strong_sections"],
            weak_sections=analysis["weak_sections"],
            unnecessary_content=analysis["unnecessary_content"],
            improvement_suggestions=analysis["improvement_suggestions"],
            is_premium=True
        )
        
    except Exception as e:
        logger.error(f"Error in premium analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )
