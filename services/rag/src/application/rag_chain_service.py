"""RAG chain service for processing chat queries with retrieval-augmented generation."""

from __future__ import annotations

import json
import time
from typing import Optional, AsyncIterator

from loguru import logger

from domain.ports import (
    VectorStorePort,
    EmbeddingPort,
    LLMGatewayPort,
    CachePort,
    Message,
    SearchResult,
)
from schemas import SourceDocument


class RAGChainService:
    """RAG chain service that orchestrates retrieval and generation."""

    def __init__(
        self,
        vector_store: VectorStorePort,
        embedding: EmbeddingPort,
        llm: LLMGatewayPort,
        cache: CachePort,
        top_k: int = 5,
    ):
        self._vector_store = vector_store
        self._embedding = embedding
        self._llm = llm
        self._cache = cache
        self._top_k = top_k

    async def chat(
        self,
        query: str,
        session_id: str,
        doc_ids: Optional[list[str]] = None,
        chat_history: Optional[list[Message]] = None,
        temperature: float = 0.7,
    ) -> tuple[str, list[SourceDocument]]:
        """
        Process a chat query with RAG.

        Returns:
            Tuple of (answer, source_documents)
        """
        start_time = time.time()

        # Check cache first
        cache_key = f"chat:{session_id}:{hash(query)}"
        cached_response = await self._cache.get(cache_key)
        if cached_response:
            logger.debug(f"Cache hit for query: {query[:50]}...")
            cached_data = json.loads(cached_response.value)
            sources = [SourceDocument(**s) for s in cached_data["sources"]]
            return cached_data["answer"], sources

        # Generate query embedding
        query_embedding = await self._embedding.async_embed_query(query)

        # Search for relevant documents
        search_results = await self._vector_store.search(
            query_vector=query_embedding,
            top_k=self._top_k,
            filter_conditions={"doc_ids": doc_ids} if doc_ids else None,
        )

        # Build context from search results
        context = self._build_context(search_results)
        sources = self._convert_sources(search_results)

        # Build messages for LLM
        messages = self._build_messages(query, context, chat_history or [])

        # Generate response
        response = await self._llm.generate(
            messages=messages,
            temperature=temperature,
        )

        # Cache the response
        await self._cache.set(
            key=cache_key,
            value=json.dumps({
                "answer": response.content,
                "sources": [s.model_dump() for s in sources],
            }),
            ttl=3600,  # 1 hour
        )

        processing_time = (time.time() - start_time) * 1000
        logger.info(f"Chat processed in {processing_time:.2f}ms")

        return response.content, sources

    async def stream_chat(
        self,
        query: str,
        session_id: str,
        doc_ids: Optional[list[str]] = None,
        chat_history: Optional[list[Message]] = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream chat response token by token.

        Yields:
            Response chunks
        """
        # Generate query embedding
        query_embedding = await self._embedding.async_embed_query(query)

        # Search for relevant documents
        search_results = await self._vector_store.search(
            query_vector=query_embedding,
            top_k=self._top_k,
            filter_conditions={"doc_ids": doc_ids} if doc_ids else None,
        )

        # Build context from search results
        context = self._build_context(search_results)
        sources = self._convert_sources(search_results)

        # Build messages for LLM
        messages = self._build_messages(query, context, chat_history or [])

        # Stream response
        async for chunk in self._llm.stream_generate(
            messages=messages,
            temperature=temperature,
        ):
            yield chunk

        # Cache the full response after streaming completes
        # Note: This is a simplified implementation

    def _build_context(self, search_results: list[SearchResult]) -> str:
        """Build context string from search results."""
        if not search_results:
            return "No relevant documents found."

        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Document {i}]\n{result.text}\n"
                f"Source: {result.payload.get('source', 'Unknown')}\n"
            )
        return "\n---\n".join(context_parts)

    def _convert_sources(self, search_results: list[SearchResult]) -> list[SourceDocument]:
        """Convert search results to source documents."""
        return [
            SourceDocument(
                text=result.text[:500],  # Truncate for source display
                score=result.score,
                metadata=result.payload,
            )
            for result in search_results
        ]

    def _build_messages(
        self,
        query: str,
        context: str,
        chat_history: list[Message],
    ) -> list[Message]:
        """Build messages for LLM with context and history."""
        system_message = Message(
            role="system",
            content=(
                "You are a helpful AI assistant. Use the provided context to answer the user's question. "
                "If the context doesn't contain relevant information, say so. "
                "Always cite your sources when using information from the context."
            ),
        )

        context_message = Message(
            role="system",
            content=f"Context:\n{context}",
        )

        # Convert chat history to Message objects if needed
        history_messages = []
        for msg in chat_history:
            if isinstance(msg, dict):
                history_messages.append(Message(role=msg["role"], content=msg["content"]))
            else:
                history_messages.append(msg)

        user_message = Message(role="user", content=query)

        return [system_message, context_message] + history_messages + [user_message]
