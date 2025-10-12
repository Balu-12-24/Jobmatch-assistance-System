"""
Database initialization script.
Creates all tables and indexes in NeonDB.
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.core.database import engine, Base, init_db
from app.models import User, UserProfile, Job, SavedJob, Company, IndianSalaryData
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes():
    """Create additional indexes for performance"""
    with engine.connect() as conn:
        try:
            # Index on saved_jobs for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_job 
                ON saved_jobs(user_id, job_id);
            """))
            
            # Index on user_profiles for user lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id 
                ON user_profiles(user_id);
            """))
            
            # Unique constraint on saved_jobs
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS unique_user_job 
                ON saved_jobs(user_id, job_id);
            """))
            
            # Indexes for Indian market fields on jobs table
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_jobs_city_tier 
                ON jobs(city_tier);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_jobs_company_type 
                ON jobs(company_type);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_jobs_country 
                ON jobs(country);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_jobs_salary_currency 
                ON jobs(salary_currency);
            """))
            
            # Indexes for Indian salary data table
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_indian_salary_job_title 
                ON indian_salary_data(job_title);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_indian_salary_experience 
                ON indian_salary_data(experience_years);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_indian_salary_location 
                ON indian_salary_data(location);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_indian_salary_company_type 
                ON indian_salary_data(company_type);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_indian_salary_industry 
                ON indian_salary_data(industry);
            """))
            
            conn.commit()
            logger.info("Additional indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            conn.rollback()


def main():
    """Main initialization function"""
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        logger.info("Creating tables...")
        init_db()
        
        # Create additional indexes
        logger.info("Creating indexes...")
        create_indexes()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
