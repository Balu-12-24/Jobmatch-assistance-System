from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate semantic embeddings using Sentence-BERT.
    Uses 'all-MiniLM-L6-v2' model for fast, high-quality embeddings.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super(EmbeddingGenerator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model
                       Default: 'all-MiniLM-L6-v2' (384 dimensions, fast)
        """
        if self._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            try:
                self._model = SentenceTransformer(model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self.get_dimension()}")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text string
            
        Returns:
            Normalized numpy array of shape (384,)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return np.zeros(self.get_dimension())
        
        try:
            # Generate embedding
            embedding = self._model.encode(text, convert_to_numpy=True)
            
            # Normalize for cosine similarity
            embedding = self._normalize(embedding)
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of text strings
            
        Returns:
            Normalized numpy array of shape (n, 384)
        """
        if not texts:
            logger.warning("Empty text list provided for batch embedding")
            return np.array([])
        
        try:
            # Generate embeddings in batch
            embeddings = self._model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )
            
            # Normalize each embedding
            embeddings = np.array([self._normalize(emb) for emb in embeddings])
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def _normalize(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalize embedding vector for cosine similarity.
        
        Args:
            embedding: Input embedding vector
            
        Returns:
            Normalized embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        return self._model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (higher is more similar)
        """
        # Cosine similarity (dot product of normalized vectors)
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)


# Global instance
_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """
    Get or create the global embedding generator instance.
    
    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
