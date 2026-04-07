"""
Script to seed Indian jobs into database and Qdrant vector store.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import json
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.job import Job
from app.services.embedding_generator import EmbeddingGenerator
from app.services.vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_job_data(file_path: str):
    """Load job data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def seed_jobs(db: Session, jobs_data: list, embedding_gen: EmbeddingGenerator, vector_store: VectorStore):
    """
    Seed jobs into database and vector store using batch processing.
    
    Args:
        db: Database session
        jobs_data: List of job dictionaries
        embedding_gen: Embedding generator instance
        vector_store: Vector store instance
    """
    logger.info(f"Seeding {len(jobs_data)} jobs with batch processing...")
    
    jobs_created = 0
    jobs_skipped = 0
    embeddings_created = 0
    
    BATCH_SIZE = 100
    
    for batch_start in range(0, len(jobs_data), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(jobs_data))
        batch = jobs_data[batch_start:batch_end]
        
        logger.info(f"Processing batch {batch_start//BATCH_SIZE + 1}/{(len(jobs_data)-1)//BATCH_SIZE + 1} ({batch_start+1}-{batch_end}/{len(jobs_data)})")
        
        batch_jobs = []
        batch_embeddings = []
        batch_vector_ids = []
        batch_metadata = []
        
        try:
            for job_data in batch:
                try:
                    # Check if job already exists
                    existing_job = db.query(Job).filter(
                        Job.title == job_data['title'],
                        Job.company == job_data['company'],
                        Job.location == job_data['location']
                    ).first()
                    
                    if existing_job:
                        jobs_skipped += 1
                        continue
                    
                    # Create job description text for embedding
                    job_text = f"{job_data['title']} {job_data['description']} {job_data['requirements']}"
                    
                    # Generate embedding
                    embedding = embedding_gen.generate_embedding(job_text)
                    
                    # Create job in database
                    new_job = Job(
                        title=job_data['title'],
                        company=job_data['company'],
                        description=job_data['description'],
                        requirements=job_data.get('requirements', ''),
                        location=job_data['location'],
                        country=job_data.get('country', 'India'),
                        city_tier=job_data.get('city_tier', 1),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency', 'INR'),
                        job_type=job_data.get('job_type', 'full-time'),
                        remote_option=job_data.get('remote_option', 'onsite'),
                        company_size=job_data.get('company_size', 'medium'),
                        company_type=job_data.get('company_type', 'service'),
                        industry=job_data.get('industry', 'Technology')
                    )
                    
                    db.add(new_job)
                    batch_jobs.append(new_job)
                    batch_embeddings.append(embedding)
                
                except Exception as e:
                    logger.error(f"Error processing job {job_data.get('title', 'Unknown')}: {e}")
                    continue
            
            # Flush to get IDs for all jobs in batch
            db.flush()
            
            # Prepare vector data for batch upload
            for job, embedding in zip(batch_jobs, batch_embeddings):
                vector_id = f"job_{job.id}"
                job.vector_id = vector_id
                
                batch_vector_ids.append(vector_id)
                batch_metadata.append({
                    "job_id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "city_tier": job.city_tier,
                    "company_type": job.company_type,
                    "salary_min": job.salary_min or 0,
                    "salary_max": job.salary_max or 0
                })
            
            # Batch upload to Qdrant
            if batch_embeddings:
                vector_store.add_vectors(
                    vectors=batch_embeddings,
                    ids=batch_vector_ids,
                    metadata=batch_metadata
                )
                embeddings_created += len(batch_embeddings)
            
            # Commit batch
            db.commit()
            jobs_created += len(batch_jobs)
            
            logger.info(f"✓ Batch completed: {len(batch_jobs)} jobs created, {jobs_skipped} skipped so far")
        
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            db.rollback()
            continue
    
    logger.info(f"\n✅ Seeding completed!")
    logger.info(f"   Jobs created: {jobs_created}")
    logger.info(f"   Jobs skipped (already exist): {jobs_skipped}")
    logger.info(f"   Embeddings created: {embeddings_created}")
    
    return jobs_created, jobs_skipped


def verify_seeding(db: Session, vector_store: VectorStore):
    """Verify that jobs were seeded correctly"""
    logger.info("\nVerifying seeding...")
    
    # Check database
    total_jobs = db.query(Job).count()
    indian_jobs = db.query(Job).filter(Job.country == 'India').count()
    jobs_with_vectors = db.query(Job).filter(Job.vector_id.isnot(None)).count()
    
    logger.info(f"Database verification:")
    logger.info(f"  Total jobs: {total_jobs}")
    logger.info(f"  Indian jobs: {indian_jobs}")
    logger.info(f"  Jobs with vector IDs: {jobs_with_vectors}")
    
    # Check by city tier
    tier1_jobs = db.query(Job).filter(Job.city_tier == 1).count()
    tier2_jobs = db.query(Job).filter(Job.city_tier == 2).count()
    tier3_jobs = db.query(Job).filter(Job.city_tier == 3).count()
    
    logger.info(f"\nJobs by city tier:")
    logger.info(f"  Tier 1: {tier1_jobs}")
    logger.info(f"  Tier 2: {tier2_jobs}")
    logger.info(f"  Tier 3: {tier3_jobs}")
    
    # Check by company type
    from sqlalchemy import func
    company_types = db.query(Job.company_type, func.count(Job.id)).group_by(Job.company_type).all()
    logger.info(f"\nJobs by company type:")
    for company_type, count in company_types:
        logger.info(f"  {company_type}: {count}")
    
    # Sample some jobs
    sample_jobs = db.query(Job).limit(3).all()
    logger.info(f"\nSample jobs:")
    for job in sample_jobs:
        logger.info(f"  - {job.title} at {job.company} ({job.location})")
        logger.info(f"    Salary: ₹{job.salary_min:,} - ₹{job.salary_max:,} {job.salary_currency}")
        logger.info(f"    City Tier: {job.city_tier}, Company Type: {job.company_type}")


def main():
    """Main seeding function"""
    try:
        logger.info("Starting Indian jobs seeding process...")
        
        # Initialize services
        logger.info("Initializing services...")
        embedding_gen = EmbeddingGenerator()
        
        # Initialize vector store (Qdrant)
        from app.core.config import settings
        vector_store = VectorStore(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name="jobs"
        )
        
        # Create collection if it doesn't exist
        try:
            vector_store.create_collection(dimension=384)
            logger.info("Qdrant collection created/verified")
        except Exception as e:
            logger.info(f"Collection may already exist: {e}")
        
        # Load job data
        logger.info("Loading job data...")
        data_dir = Path(__file__).parent.parent / "data"
        
        # Try to load full Indian jobs first
        indian_jobs_path = data_dir / "indian_jobs_full.json"
        if indian_jobs_path.exists():
            jobs_data = load_job_data(str(indian_jobs_path))
            logger.info(f"Loaded {len(jobs_data)} jobs from indian_jobs_full.json")
        else:
            # Fallback to manual Indian jobs
            indian_jobs_path = data_dir / "indian_jobs.json"
            if indian_jobs_path.exists():
                jobs_data = load_job_data(str(indian_jobs_path))
                logger.info(f"Loaded {len(jobs_data)} jobs from indian_jobs.json")
            else:
                logger.error("No Indian jobs data file found!")
                logger.info("Please run: python backend/scripts/generate_indian_jobs.py")
                return
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Seed jobs
            jobs_created, jobs_skipped = seed_jobs(db, jobs_data, embedding_gen, vector_store)
            
            # Verify seeding
            verify_seeding(db, vector_store)
            
            logger.info("\n✅ Indian jobs seeding completed successfully!")
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error in seeding process: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
