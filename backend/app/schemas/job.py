from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    remote_option: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None


class JobResponse(JobBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    job: JobResponse
    compatibility_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    salary_prediction: Optional[dict] = None
    company_fit_score: Optional[float] = None
    company_fit_explanation: Optional[str] = None


class JobRecommendationsResponse(BaseModel):
    matches: List[JobMatchResponse]
    total_count: int
