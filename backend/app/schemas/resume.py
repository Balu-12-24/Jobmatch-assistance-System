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


class ATSScore(BaseModel):
    """ATS Score breakdown by category"""
    overall_score: int
    formatting_score: int
    keywords_score: int
    experience_score: int
    education_score: int
    readability_score: int


class StrongSection(BaseModel):
    """Strong section of resume"""
    section: str
    reason: str
    examples: List[str]


class WeakSection(BaseModel):
    """Weak section needing improvement"""
    section: str
    issue: str
    suggestions: List[str]


class ResumeAnalysisResponse(BaseModel):
    """Complete resume analysis response"""
    ats_score: ATSScore
    strong_sections: List[StrongSection]
    weak_sections: List[WeakSection]
    unnecessary_content: List[str]
    improvement_suggestions: List[str]
    is_premium: bool


class JobComparisonRequest(BaseModel):
    """Request to compare resume with job description"""
    job_description: str


class JobComparisonResponse(BaseModel):
    """Job comparison analysis response"""
    matching_keywords: List[str]
    missing_keywords: List[str]
    keyword_match_percentage: float
    suggestions: List[str]
    is_premium: bool
