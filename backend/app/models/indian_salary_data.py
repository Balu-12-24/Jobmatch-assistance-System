from sqlalchemy import Column, Integer, String, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class IndianSalaryData(Base):
    __tablename__ = "indian_salary_data"
    
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), index=True)
    experience_years = Column(Integer, index=True)
    location = Column(String(255), index=True)
    city_tier = Column(Integer)  # 1, 2, 3
    company_type = Column(String(50), index=True)  # MNC, startup, service, product, BPO, KPO
    skills = Column(JSONB)  # JSON array of skills
    salary_lpa = Column(DECIMAL(10, 2))  # Lakhs Per Annum
    salary_inr_annual = Column(Integer)  # Annual salary in INR
    industry = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
