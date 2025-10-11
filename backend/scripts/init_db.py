"""
Database initialization script.
Creates all tables and indexes in NeonDB.
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine, Base, init_db
from app.models import User, UserProfile, Job, SavedJob, Company
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
