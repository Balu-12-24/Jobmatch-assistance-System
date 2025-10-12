from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    location = Column(String(255), index=True)
    country = Column(String(50), default='India')
    city_tier = Column(Integer)  # 1, 2, 3 for Indian cities
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default='INR')  # INR, USD, etc.
    job_type = Column(String(50))  # full-time, part-time, contract
    remote_option = Column(String(50), index=True)  # remote, hybrid, onsite
    company_size = Column(String(50))
    company_type = Column(String(50))  # MNC, startup, service, product, BPO, KPO
    industry = Column(String(100), index=True)
    vector_id = Column(String(255))  # Reference to vector in Qdrant
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    compatibility_score = Column(Integer)  # 0-100
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='unique_user_job'),
    )
