"""Qdrant client for vector operations."""

import uuid
import asyncio
from functools import partial
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import structlog

from app.config import settings
from app.core.exceptions import QdrantException, ErrorCode

logger = structlog.get_logger()

class QdrantService:
    """Async Qdrant service with connection management and retry logic."""
    
    def __init__(self):
        self._client: Optional[QdrantClient] = None
    
    def get_client(self) -> QdrantClient:
        """Get or create Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=30.0
            )
        return self._client
    
    def close(self):
        """Close the Qdrant client."""
        if self._client:
            try:
                self._client.close()
            except:
                pass  # Ignore close errors
            self._client = None

# Global service instance
_qdrant_service = QdrantService()

def get_qdrant_service() -> QdrantService:
    """Get the global Qdrant service instance."""
    return _qdrant_service


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def create_collection(collection_name: str, vector_size: int = 1536) -> bool:
    """
    Create a new Qdrant collection with retry logic.
    
    Args:
        collection_name: Name of the collection
        vector_size: Dimension of vectors (default 1536 for text-embedding-3-large)
        
    Returns:
        True if successful
        
    Raises:
        QdrantException: If collection creation fails after retries
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        logger.info("qdrant.collection.create_request", collection=collection_name, size=vector_size)
        
        # Run synchronous operations in executor
        loop = asyncio.get_event_loop()
        
        # Check if collection already exists
        get_collections_func = partial(client.get_collections)
        collections_response = await loop.run_in_executor(None, get_collections_func)
        collections = collections_response.collections
        
        if any(c.name == collection_name for c in collections):
            logger.info("qdrant.collection.exists", collection=collection_name)
            return True
        
        # Create collection
        create_func = partial(
            client.create_collection,
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        await loop.run_in_executor(None, create_func)
        
        logger.info("qdrant.collection.created", collection=collection_name, size=vector_size)
        return True
        
    except Exception as e:
        logger.error("qdrant.collection.create_failed", 
                    collection=collection_name, error=str(e))
        raise QdrantException(
            message=f"Failed to create collection: {collection_name}",
            details={"collection": collection_name, "vector_size": vector_size, "error": str(e)}
        ) from e


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def upsert_vector(
    collection_name: str,
    point_id: str,
    vector: List[float],
    payload: Dict[str, Any]
) -> bool:
    """
    Upsert a vector into Qdrant collection with retry logic.
    
    Args:
        collection_name: Name of the collection
        point_id: Unique ID for the point
        vector: Embedding vector
        payload: Metadata to store with the vector
        
    Returns:
        True if successful
        
    Raises:
        QdrantException: If vector upsert fails after retries
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        logger.info("qdrant.vector.upsert_request", 
                   collection=collection_name, point_id=point_id, 
                   vector_size=len(vector))
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )
        
        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        upsert_func = partial(
            client.upsert,
            collection_name=collection_name,
            points=[point]
        )
        await loop.run_in_executor(None, upsert_func)
        
        logger.info("qdrant.vector.upserted", 
                   collection=collection_name, point_id=point_id)
        return True
        
    except Exception as e:
        logger.error("qdrant.vector.upsert_failed", 
                    collection=collection_name, point_id=point_id, error=str(e))
        raise QdrantException(
            message=f"Failed to upsert vector to collection: {collection_name}",
            details={
                "collection": collection_name, 
                "point_id": point_id, 
                "vector_size": len(vector),
                "error": str(e)
            }
        ) from e


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def search_vectors(
    collection_name: str,
    query_vector: List[float],
    top_k: int = 10,
    score_threshold: Optional[float] = None,
    filter_conditions: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar vectors in a collection with retry logic.
    
    Args:
        collection_name: Name of the collection
        query_vector: Query embedding vector
        top_k: Number of results to return
        score_threshold: Minimum similarity score
        filter_conditions: Optional filters for the search
        
    Returns:
        List of search results with scores and payloads
        
    Raises:
        QdrantException: If vector search fails after retries
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        logger.info("qdrant.search.request", 
                   collection=collection_name, top_k=top_k, 
                   has_filters=bool(filter_conditions),
                   score_threshold=score_threshold)
        
        # Build filter if provided
        query_filter = None
        if filter_conditions:
            conditions = []
            for key, value in filter_conditions.items():
                if isinstance(value, list):
                    # Match any value in the list
                    for v in value:
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=v))
                        )
                else:
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            
            if conditions:
                query_filter = Filter(should=conditions)
        
        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        search_func = partial(
            client.search,
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
            score_threshold=score_threshold,
            with_payload=True
        )
        search_result = await loop.run_in_executor(None, search_func)
        
        # Format results
        results = []
        for hit in search_result:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            })
        
        logger.info("qdrant.search.success", 
                   collection=collection_name, results_count=len(results))
        
        return results
        
    except Exception as e:
        logger.error("qdrant.search.failed", 
                    collection=collection_name, error=str(e))
        raise QdrantException(
            message=f"Failed to search vectors in collection: {collection_name}",
            details={
                "collection": collection_name,
                "top_k": top_k,
                "has_filters": bool(filter_conditions), 
                "error": str(e)
            }
        ) from e


async def delete_vector(collection_name: str, point_id: str) -> bool:
    """
    Delete a vector from a collection.
    
    Args:
        collection_name: Name of the collection
        point_id: ID of the point to delete
        
    Returns:
        True if successful
        
    Raises:
        QdrantException: If vector deletion fails
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        logger.info("qdrant.vector.delete_request", 
                   collection=collection_name, point_id=point_id)
        
        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        delete_func = partial(
            client.delete,
            collection_name=collection_name,
            points_selector=[point_id]
        )
        await loop.run_in_executor(None, delete_func)
        
        logger.info("qdrant.vector.deleted", 
                   collection=collection_name, point_id=point_id)
        return True
        
    except Exception as e:
        logger.error("qdrant.vector.delete_failed", 
                    collection=collection_name, point_id=point_id, error=str(e))
        raise QdrantException(
            message=f"Failed to delete vector from collection: {collection_name}",
            details={"collection": collection_name, "point_id": point_id, "error": str(e)}
        ) from e


async def collection_exists(collection_name: str) -> bool:
    """
    Check if a collection exists.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        True if collection exists
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        get_collections_func = partial(client.get_collections)
        collections_response = await loop.run_in_executor(None, get_collections_func)
        collections = collections_response.collections
        
        exists = any(c.name == collection_name for c in collections)
        logger.info("qdrant.collection.exists_check", 
                   collection=collection_name, exists=exists)
        return exists
        
    except Exception as e:
        logger.warning("qdrant.collection.exists_check_failed", 
                      collection=collection_name, error=str(e))
        return False


async def test_qdrant_connection() -> bool:
    """
    Test if Qdrant is accessible.
    
    Returns:
        True if connection is successful
    """
    try:
        service = get_qdrant_service()
        client = service.get_client()
        
        # Run synchronous operation in executor
        loop = asyncio.get_event_loop()
        get_collections_func = partial(client.get_collections)
        await loop.run_in_executor(None, get_collections_func)
        
        logger.info("qdrant.connection_test.success")
        return True
        
    except Exception as e:
        logger.warning("qdrant.connection_test.failed", error=str(e))
        return False



