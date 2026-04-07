"""
Fix script to generate and upload embeddings for existing jobs to Qdrant.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.core.database import SessionLocal
from app.models.job import Job
from app.services.embedding_generator import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Generate and upload embeddings for all existing jobs"""
    db = SessionLocal()
    
    try:
        logger.info("Initializing services...")
        embedding_gen = EmbeddingGenerator()
        vector_store = VectorStore(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name='jobs'
        )
        
        # Get all jobs
        jobs = db.query(Job).all()
        logger.info(f"Found {len(jobs)} jobs in database")
        
        if not jobs:
            logger.error("No jobs found in database!")
            return
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        texts = [f"{j.title} {j.description} {j.requirements}" for j in jobs]
        embeddings = []
        
        for i, text in enumerate(texts):
            if i % 50 == 0:
                logger.info(f"Processing job {i+1}/{len(texts)}...")
            embedding = embedding_gen.generate_embedding(text)
            embeddings.append(embedding)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Prepare data for Qdrant
        vector_ids = [f"job_{j.id}" for j in jobs]
        metadata = [
            {
                "job_id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "city_tier": j.city_tier,
                "company_type": j.company_type,
                "salary_min": j.salary_min or 0,
                "salary_max": j.salary_max or 0
            }
            for j in jobs
        ]
        
        # Upload to Qdrant in batches to avoid timeout
        logger.info("Uploading embeddings to Qdrant in batches...")
        BATCH_SIZE = 50
        total_uploaded = 0
        
        for i in range(0, len(embeddings), BATCH_SIZE):
            batch_end = min(i + BATCH_SIZE, len(embeddings))
            batch_embeddings = embeddings[i:batch_end]
            batch_ids = vector_ids[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            
            logger.info(f"Uploading batch {i//BATCH_SIZE + 1}/{(len(embeddings)-1)//BATCH_SIZE + 1} ({i+1}-{batch_end}/{len(embeddings)})")
            
            vector_store.add_vectors(
                vectors=batch_embeddings,
                ids=batch_ids,
                metadata=batch_metadata
            )
            total_uploaded += len(batch_embeddings)
        
        logger.info(f"✅ Successfully uploaded {total_uploaded} embeddings to Qdrant!")
        logger.info("You can now refresh your dashboard to see job recommendations.")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
