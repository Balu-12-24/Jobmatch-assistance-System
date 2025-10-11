from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional, Tuple
import numpy as np
from app.core.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store using Qdrant Cloud for job embeddings.
    Handles storage, search, and filtering of job vectors.
    """
    
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = None
    ):
        """
        Initialize Qdrant client and collection.
        
        Args:
            url: Qdrant Cloud URL (defaults to settings)
            api_key: Qdrant API key (defaults to settings)
            collection_name: Collection name (defaults to settings)
        """
        self.url = url or settings.QDRANT_URL
        self.api_key = api_key or settings.QDRANT_API_KEY
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        
        try:
            # For Qdrant Cloud, extract host from URL and use port 443
            # Remove https:// prefix if present
            host = self.url.replace('https://', '').replace('http://', '')
            # Remove any port if present
            host = host.split(':')[0]
            
            self.client = QdrantClient(
                host=host,
                port=443,
                api_key=self.api_key,
                https=True
            )
            logger.info(f"Connected to Qdrant at {host}:443")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {e}")
            raise
    
    def create_collection(self, dimension: int = 384):
        """
        Create a collection for job embeddings.
        
        Args:
            dimension: Dimension of embedding vectors (default: 384 for all-MiniLM-L6-v2)
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return
            
            # Create collection with cosine distance
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}' with dimension {dimension}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: List[int],
        metadata: List[Dict]
    ) -> List[str]:
        """
        Add job vectors to the collection.
        
        Args:
            vectors: Numpy array of shape (n, dimension)
            ids: List of job IDs from database
            metadata: List of metadata dicts (title, company, location, etc.)
            
        Returns:
            List of vector IDs in Qdrant
        """
        try:
            points = []
            vector_ids = []
            
            for i, (vector, job_id, meta) in enumerate(zip(vectors, ids, metadata)):
                # Generate unique vector ID
                vector_id = str(uuid.uuid4())
                vector_ids.append(vector_id)
                
                # Create point with vector and metadata
                point = PointStruct(
                    id=vector_id,
                    vector=vector.tolist(),
                    payload={
                        "job_id": job_id,
                        **meta  # Include all metadata
                    }
                )
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} vectors to collection '{self.collection_name}'")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            raise
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar job vectors.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            filter_dict: Optional filters (e.g., {"location": "New York", "remote_option": "remote"})
            
        Returns:
            List of tuples: (vector_id, similarity_score, metadata)
        """
        try:
            # For now, skip filters to avoid Qdrant index errors
            # Filters can be applied post-search in the application layer
            
            # Search without filters
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector,
                limit=k * 2  # Get more results to allow for post-filtering
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append((
                    result.id,
                    result.score,
                    result.payload
                ))
            
            # Apply filters in Python if provided
            if filter_dict:
                filtered_results = []
                for vector_id, score, payload in formatted_results:
                    match = True
                    for key, value in filter_dict.items():
                        if value is not None and payload.get(key) != value:
                            match = False
                            break
                    if match:
                        filtered_results.append((vector_id, score, payload))
                formatted_results = filtered_results[:k]
            else:
                formatted_results = formatted_results[:k]
            
            logger.info(f"Found {len(formatted_results)} similar vectors")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise
    
    def delete_vector(self, vector_id: str):
        """
        Delete a vector from the collection.
        
        Args:
            vector_id: ID of the vector to delete
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[vector_id]
            )
            logger.info(f"Deleted vector {vector_id}")
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            raise
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance.
    
    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        # Ensure collection exists
        try:
            _vector_store.create_collection()
        except Exception as e:
            logger.warning(f"Could not create collection (may already exist): {e}")
    return _vector_store
