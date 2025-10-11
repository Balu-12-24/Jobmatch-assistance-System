"""
Seed demo users for testing and demonstration.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserProfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo_users():
    """Create demo user accounts"""
    db = SessionLocal()
    
    demo_users = [
        {
            "email": "demo@jobmatch.ai",
            "password": "demo123",
            "full_name": "Demo User",
            "is_premium": False,
            "skills": ["Python", "JavaScript", "React", "FastAPI", "SQL"],
            "experience_years": 3,
            "education_level": "bachelor",
            "location": "San Francisco, CA",
            "preferences": {
                "remote_option": "hybrid",
                "company_size": "medium",
                "industry": "technology"
            }
        },
        {
            "email": "premium@jobmatch.ai",
            "password": "premium123",
            "full_name": "Premium User",
            "is_premium": True,
            "skills": ["Machine Learning", "Python", "TensorFlow", "PyTorch", "NLP", "Data Analysis"],
            "experience_years": 5,
            "education_level": "master",
            "location": "New York, NY",
            "preferences": {
                "remote_option": "remote",
                "company_size": "startup",
                "industry": "artificial intelligence"
            }
        },
        {
            "email": "john@example.com",
            "password": "password123",
            "full_name": "John Developer",
            "is_premium": False,
            "skills": ["Java", "Spring Boot", "Microservices", "Docker", "Kubernetes"],
            "experience_years": 4,
            "education_level": "bachelor",
            "location": "Austin, TX",
            "preferences": {
                "remote_option": "onsite",
                "company_size": "large",
                "industry": "enterprise software"
            }
        }
    ]
    
    try:
        for user_data in demo_users:
            # Check if user exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                logger.info(f"User {user_data['email']} already exists, skipping")
                continue
            
            # Create user
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_premium=user_data["is_premium"]
            )
            db.add(user)
            db.flush()
            
            # Create profile
            profile = UserProfile(
                user_id=user.id,
                skills=user_data["skills"],
                experience_years=user_data["experience_years"],
                education_level=user_data["education_level"],
                location=user_data["location"],
                preferences=user_data["preferences"],
                resume_text=f"Sample resume for {user_data['full_name']} with {user_data['experience_years']} years of experience in {', '.join(user_data['skills'][:3])}."
            )
            db.add(profile)
            
            logger.info(f"Created user: {user_data['email']} (password: {user_data['password']})")
        
        db.commit()
        logger.info("✅ Demo users created successfully!")
        logger.info("\nDemo Accounts:")
        logger.info("1. demo@jobmatch.ai / demo123 (Free tier)")
        logger.info("2. premium@jobmatch.ai / premium123 (Premium tier)")
        logger.info("3. john@example.com / password123 (Free tier)")
        
    except Exception as e:
        logger.error(f"Error creating demo users: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()
