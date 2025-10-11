from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.resume_parser import ResumeParser
from app.schemas.resume import ResumeUploadResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

# Initialize resume parser
resume_parser = ResumeParser()

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
