# Database models
from .user import User, UserProfile
from .job import Job, SavedJob
from .company import Company
from .indian_salary_data import IndianSalaryData

__all__ = ["User", "UserProfile", "Job", "SavedJob", "Company", "IndianSalaryData"]
