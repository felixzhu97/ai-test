"""Qdrant vector store adapter - implements VectorStorePort interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
import uuid

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

from domain.ports.vector_store import VectorStorePort, SearchResult


def _get_settings():
    """Lazy import settings to avoid circular imports."""
    from config import get_settings
    return get_settings()


class QdrantVectorStoreAdapter(VectorStorePort):
    """Qdrant vector storage adapter implementing VectorStorePort interface."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        settings = _get_settings()
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.client: Optional[QdrantClient] = None
        self._embedding_size: Optional[int] = None

    def _connect(self) -> QdrantClient:
        """Establish connection to Qdrant server."""
        if self.client is None:
            url = f"http://{self.host}:{self.port}"
            self.client = QdrantClient(url=url, check_compatibility=False)
        return self.client

    @property
    def embedding_size(self) -> int:
        """Get embedding dimension from configuration."""
        if self._embedding_size is None:
            from src.core.embedding import get_embedding_model
            model = get_embedding_model()
            self._embedding_size = model.dimension
        return self._embedding_size

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_conditions: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        try:
            client = self._connect()

            search_filter = None
            if filter_conditions and "doc_ids" in filter_conditions:
                doc_ids = filter_conditions["doc_ids"]
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchAny(any=doc_ids),
                        )
                    ]
                )

            # Use old API compatible with Qdrant 1.7.4
            search_request = SearchRequest(
                vector=query_vector,
                limit=top_k,
                filter=search_filter,
                with_payload=True,
            )

            results = client.http.search_api.search_points(
                collection_name=self.collection_name,
                search_request=search_request,
            )

            return [
                SearchResult(
                    id=str(hit.id),
                    text=hit.payload.get("text", ""),
                    score=hit.score,
                    payload=hit.payload or {},
                )
                for hit in results.result
            ]
        except UnexpectedResponse as e:
            if e.status_code == 404:
                # Collection doesn't exist, return empty results
                return []
            raise

    async def upsert(
        self,
        vectors: list[list[float]],
        texts: list[str],
        payloads: list[dict[str, Any]],
        batch_size: int = 100,
    ) -> list[str]:
        """Batch insert or update vectors."""
        client = self._connect()

        if not await self.collection_exists(self.collection_name):
            await self.create_collection(
                self.collection_name,
                len(vectors[0]) if vectors else 1536,
            )

        ids = [str(uuid.uuid4()) for _ in vectors]

        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i : i + batch_size]
            batch_texts = texts[i : i + batch_size]
            batch_payloads = payloads[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]

            points = [
                PointStruct(
                    id=batch_id,
                    vector=vec,
                    payload={
                        "text": text,
                        **payload,
                    },
                )
                for batch_id, vec, text, payload in zip(batch_ids, batch_vectors, batch_texts, batch_payloads)
            ]

            client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

        return ids

    async def delete(self, doc_id: str) -> bool:
        """Delete all vectors associated with a document."""
        return await self.delete_by_filter({"doc_id": doc_id}) > 0

    async def delete_by_filter(self, filter_conditions: dict[str, Any]) -> int:
        """Delete vectors matching filter conditions."""
        client = self._connect()

        doc_id = filter_conditions.get("doc_id")
        if not doc_id:
            return 0

        client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id),
                    )
                ]
            ),
        )

        return 1

    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        client = self._connect()
        try:
            client.get_collection(collection_name)
            return True
        except (UnexpectedResponse, Exception):
            return False

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "Cosine",
    ) -> bool:
        """Create a new collection."""
        client = self._connect()

        distance = Distance.COSINE if distance_metric == "Cosine" else Distance.EUCLID

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )

        return True
