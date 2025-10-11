from pydantic import BaseModel
from typing import List, Optional


class ParsedResume(BaseModel):
    raw_text: str
    skills: List[str]
    experience_years: Optional[int] = None
    education_level: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    message: str
    skills: List[str]
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    raw_text_preview: str
