"""
Job data ingestion script.
Loads sample jobs from JSON file, stores in database, and generates embeddings.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.job import Job
from app.services.embedding_generator import get_embedding_generator
from app.services.vector_store import get_vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_jobs_from_json(file_path: str):
    """Load jobs from JSON file"""
    try:
        with open(file_path, 'r') as f:
            jobs_data = json.load(f)
        logger.info(f"Loaded {len(jobs_data)} jobs from {file_path}")
        return jobs_data
    except Exception as e:
        logger.error(f"Error loading jobs from file: {e}")
        raise


def create_job_text(job_data: dict) -> str:
    """
    Create combined text for embedding generation.
    Combines title, description, and requirements.
    """
    parts = [
        f"Job Title: {job_data['title']}",
        f"Company: {job_data['company']}",
        f"Description: {job_data['description']}",
        f"Requirements: {job_data['requirements']}"
    ]
    return " ".join(parts)


def main():
    """Main ingestion function"""
    db = SessionLocal()
    
    try:
        # Load jobs from JSON
        jobs_file = Path(__file__).parent.parent / "data" / "sample_jobs.json"
        jobs_data = load_jobs_from_json(str(jobs_file))
        
        # Initialize services
        logger.info("Initializing embedding generator...")
        embedding_gen = get_embedding_generator()
        
        logger.info("Initializing vector store...")
        vector_store = get_vector_store()
        
        # Process each job
        job_objects = []
        job_texts = []
        job_ids = []
        metadata_list = []
        
        logger.info("Processing jobs...")
        for job_data in jobs_data:
            # Create job in database
            job = Job(
                title=job_data['title'],
                company=job_data['company'],
                description=job_data['description'],
                requirements=job_data.get('requirements'),
                location=job_data.get('location'),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                job_type=job_data.get('job_type'),
                remote_option=job_data.get('remote_option'),
                company_size=job_data.get('company_size'),
                industry=job_data.get('industry')
            )
            
            db.add(job)
            db.flush()  # Get the job ID
            
            job_objects.append(job)
            job_ids.append(job.id)
            
            # Prepare text for embedding
            job_text = create_job_text(job_data)
            job_texts.append(job_text)
            
            # Prepare metadata for vector store
            metadata = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "remote_option": job.remote_option,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "industry": job.industry
            }
            metadata_list.append(metadata)
            
            logger.info(f"Processed: {job.title} at {job.company}")
        
        # Commit jobs to database
        db.commit()
        logger.info(f"Saved {len(job_objects)} jobs to database")
        
        # Generate embeddings in batch
        logger.info("Generating embeddings...")
        embeddings = embedding_gen.generate_batch_embeddings(job_texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store embeddings in Qdrant
        logger.info("Storing embeddings in Qdrant...")
        vector_ids = vector_store.add_vectors(
            vectors=embeddings,
            ids=job_ids,
            metadata=metadata_list
        )
        
        # Update jobs with vector IDs
        for job, vector_id in zip(job_objects, vector_ids):
            job.vector_id = vector_id
        
        db.commit()
        logger.info(f"Updated jobs with vector IDs")
        
        logger.info("✅ Job ingestion completed successfully!")
        logger.info(f"Total jobs processed: {len(job_objects)}")
        
    except Exception as e:
        logger.error(f"Error during job ingestion: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
