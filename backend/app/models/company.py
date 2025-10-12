from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    culture_values = Column(JSONB)  # JSON array of culture values
    size = Column(String(50))  # startup, small, medium, large, enterprise
    industry = Column(String(100), index=True)
    company_type = Column(String(50))  # MNC, startup, service, product
    headquarters_country = Column(String(50))
