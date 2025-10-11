"""
Reset database - drop and recreate all tables.
WARNING: This will delete all data!
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import User, UserProfile, Job, SavedJob, Company
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """Drop and recreate all tables"""
    try:
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database reset successfully!")
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    response = input("This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        reset_database()
    else:
        logger.info("Cancelled")
