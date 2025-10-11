"""
Create Qdrant collection for job embeddings.
Run this before loading jobs.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_collection():
    """Create the jobs collection in Qdrant"""
    try:
        # Extract host from URL
        host = settings.QDRANT_URL.replace('https://', '').replace('http://', '').split(':')[0]
        
        logger.info(f"Connecting to Qdrant at {host}:443...")
        client = QdrantClient(
            host=host,
            port=443,
            api_key=settings.QDRANT_API_KEY,
            https=True
        )
        
        collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Check if collection exists
        try:
            collections = client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name in collection_names:
                logger.info(f"Collection '{collection_name}' already exists")
                
                # Ask if user wants to recreate
                response = input(f"Delete and recreate collection '{collection_name}'? (yes/no): ")
                if response.lower() == 'yes':
                    client.delete_collection(collection_name)
                    logger.info(f"Deleted collection '{collection_name}'")
                else:
                    logger.info("Keeping existing collection")
                    return
        except Exception as e:
            logger.info(f"No existing collections found: {e}")
        
        # Create collection
        logger.info(f"Creating collection '{collection_name}' with 384 dimensions...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  # Sentence-BERT all-MiniLM-L6-v2 dimension
                distance=Distance.COSINE
            )
        )
        
        logger.info(f"✅ Collection '{collection_name}' created successfully!")
        logger.info(f"You can now run: python scripts/load_jobs.py")
        
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_collection()
