"""
Test Qdrant connection with different configurations.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Test different connection methods"""
    
    host = settings.QDRANT_URL.replace('https://', '').replace('http://', '').split(':')[0]
    api_key = settings.QDRANT_API_KEY
    
    logger.info(f"Testing connection to: {host}")
    logger.info(f"API Key (first 10 chars): {api_key[:10]}...")
    
    # Test 1: Using host + port 443
    logger.info("\n=== Test 1: host + port 443 + https ===")
    try:
        client = QdrantClient(
            host=host,
            port=443,
            api_key=api_key,
            https=True
        )
        collections = client.get_collections()
        logger.info(f"✅ SUCCESS! Collections: {collections}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
    
    # Test 2: Using host + port 6333
    logger.info("\n=== Test 2: host + port 6333 + https ===")
    try:
        client = QdrantClient(
            host=host,
            port=6333,
            api_key=api_key,
            https=True
        )
        collections = client.get_collections()
        logger.info(f"✅ SUCCESS! Collections: {collections}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
    
    # Test 3: Using full URL
    logger.info("\n=== Test 3: Using full URL ===")
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=api_key
        )
        collections = client.get_collections()
        logger.info(f"✅ SUCCESS! Collections: {collections}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
    
    # Test 4: Using URL without https://
    logger.info("\n=== Test 4: Using URL without https:// ===")
    try:
        client = QdrantClient(
            url=host,
            api_key=api_key
        )
        collections = client.get_collections()
        logger.info(f"✅ SUCCESS! Collections: {collections}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
    
    logger.error("\n❌ All connection attempts failed!")
    logger.info("\nPlease verify:")
    logger.info("1. Your Qdrant cluster is RUNNING and HEALTHY")
    logger.info("2. Your API key is correct")
    logger.info("3. Your cluster URL is correct")
    return None


if __name__ == "__main__":
    test_connection()
