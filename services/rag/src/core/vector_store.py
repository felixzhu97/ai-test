from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    SearchRequest,
)
from typing import Optional, Any
from loguru import logger
from ..config import get_settings


class VectorStore:
    """Qdrant vector store wrapper for document storage and retrieval."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        dim: Optional[int] = None,
    ):
        settings = get_settings()
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.dim = dim or settings.QDRANT_VECTOR_DIM

        self.client: Optional[QdrantClient] = None
        self._connect()

    def _connect(self):
        """Establish connection to Qdrant."""
        url = f"http://{self.host}:{self.port}"
        logger.info(f"Connecting to Qdrant at {url}")
        self.client = QdrantClient(url=url)
        logger.info("Connected to Qdrant successfully")

    def create_collection(self, if_not_exists: bool = True):
        """Create the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            existing = [c.name for c in collections]
            
            if self.collection_name in existing:
                if if_not_exists:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return
                else:
                    self.client.delete_collection(collection_name=self.collection_name)

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

        except UnexpectedResponse as e:
            if "already exists" in str(e).lower():
                logger.info(f"Collection {self.collection_name} already exists")
            else:
                raise

    def insert(
        self,
        vectors: list[list[float]],
        texts: list[str],
        metadata: list[dict],
    ) -> list[str]:
        """Insert vectors with their texts and metadata."""
        if len(vectors) != len(texts) or len(texts) != len(metadata):
            raise ValueError("Vectors, texts, and metadata must have the same length")

        from uuid import uuid4
        ids = [str(uuid4()) for _ in vectors]

        points = [
            PointStruct(
                id=id_,
                vector=vector,
                payload={
                    "text": text,
                    **{k: v for k, v in meta.items() if k not in ("doc_id",)},
                    "doc_id": meta.get("doc_id"),
                },
            )
            for id_, vector, text, meta in zip(ids, vectors, texts, metadata)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(f"Inserted {len(vectors)} vectors")
        return ids

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        doc_ids: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        query_filter = None
        if doc_ids:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchAny(any=[doc_id for doc_id in doc_ids]),
                    )
                ]
            )

        search_request = SearchRequest(
            vector=query_vector,
            limit=top_k,
            with_payload=True,
            filter=query_filter,
        )

        results = self.client.http.search_api.search_points(
            collection_name=self.collection_name,
            search_request=search_request,
        )

        return [
            {
                "id": str(result.id),
                "distance": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k not in ("text",)},
            }
            for result in results.result
        ]

    def _parse_filter(self, filter_expr: str) -> dict:
        """Parse simple filter expression to Qdrant Filter model."""
        import re
        
        if 'metadata["doc_id"]' in filter_expr and '==' in filter_expr:
            match = re.search(r'==\s*"([^"]+)"', filter_expr)
            if match:
                doc_id = match.group(1)
                return {
                    "must": [
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                }
        return {}

    def delete_by_ids(self, ids: list[str]):
        """Delete vectors by their IDs."""
        from qdrant_client.models import PointIdsList
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=ids),
        )
        logger.info(f"Deleted {len(ids)} vectors")

    def delete_by_doc_id(self, doc_id: str):
        """Delete all vectors associated with a document."""
        from qdrant_client.models import FilterSelector
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                )
            ),
        )
        logger.info(f"Deleted vectors for doc_id: {doc_id}")

    def get_all_documents(self) -> list[dict[str, Any]]:
        """Get all unique documents from the collection by scrolling through all points."""
        seen_doc_ids = set()
        documents = []
        offset = None
        
        while True:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
            )
            
            points = result[0] if isinstance(result, tuple) else result
            if not points:
                break
                
            for point in points:
                doc_id = point.payload.get("doc_id")
                if doc_id and doc_id not in seen_doc_ids:
                    seen_doc_ids.add(doc_id)
                    documents.append({
                        "doc_id": doc_id,
                        "filename": point.payload.get("filename", "Unknown"),
                        "title": point.payload.get("title", point.payload.get("filename", "Unknown")),
                        "source": point.payload.get("source", "unknown"),
                    })
            
            if isinstance(result, tuple) and len(result) > 1 and result[1]:
                offset = result[1]
            else:
                break
        
        return documents

    def get_stats(self) -> dict[str, Any]:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "total_vectors": info.points_count,
                "collection_name": self.collection_name,
                "dimension": self.dim,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def count(self) -> int:
        """Get the total number of vectors."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0

    def close(self):
        """Close the client connection."""
        self.client = None


_vector_store_instance: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance


def reset_vector_store():
    """Reset the global vector store instance."""
    global _vector_store_instance
    if _vector_store_instance:
        _vector_store_instance.close()
    _vector_store_instance = None
