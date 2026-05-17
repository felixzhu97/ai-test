"""Document service for managing document upload, ingestion, and retrieval."""

from __future__ import annotations

import uuid
from typing import Optional

from loguru import logger

from domain.ports import (
    DocumentRepositoryPort,
    VectorStorePort,
    EmbeddingPort,
    CachePort,
    DocumentRecord,
    DocumentStatus,
)
from schemas import DocumentMetadata, DocumentSource


class DocumentService:
    """Service for document management operations."""

    def __init__(
        self,
        document_repository: DocumentRepositoryPort,
        vector_store: VectorStorePort,
        embedding: EmbeddingPort,
        cache: CachePort,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        self._document_repository = document_repository
        self._vector_store = vector_store
        self._embedding = embedding
        self._cache = cache
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def _get_source_type(self, filename: str) -> DocumentSource:
        """Determine document source type from filename."""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        source_map = {
            "md": DocumentSource.MARKDOWN,
            "markdown": DocumentSource.MARKDOWN,
            "pdf": DocumentSource.PDF,
            "txt": DocumentSource.TEXT,
            "text": DocumentSource.TEXT,
            "html": DocumentSource.WEB,
            "htm": DocumentSource.WEB,
        }
        return source_map.get(ext, DocumentSource.TEXT)

    async def upload_document(
        self,
        content: bytes,
        filename: str,
        title: Optional[str] = None,
        source_type: str = "file",
    ) -> DocumentRecord:
        """
        Upload and register a document.

        Args:
            content: Document content as bytes
            filename: Original filename
            title: Optional document title
            source_type: Type of source (file, text, web)

        Returns:
            DocumentRecord with the created document info
        """
        doc_id = str(uuid.uuid4())

        record = DocumentRecord(
            doc_id=doc_id,
            title=title or filename,
            source=source_type,
            filename=filename,
            file_size=len(content),
            status=DocumentStatus.PENDING,
        )

        await self._document_repository.add(record)

        logger.info(f"Document registered: {doc_id} ({filename})")
        return record

    async def ingest_document(
        self,
        doc_id: str,
        content: bytes,
        filename: str,
    ) -> bool:
        """
        Ingest document content into vector store.

        Args:
            doc_id: Document ID
            content: Document content as bytes
            filename: Original filename

        Returns:
            True if ingestion was successful
        """
        try:
            # Update status to indexing
            await self._document_repository.update_status(doc_id, DocumentStatus.INDEXING)

            # Determine source type and use appropriate loader
            source_type = self._get_source_type(filename)
            metadata = DocumentMetadata(
                source=source_type,
                filename=filename,
                doc_id=doc_id,
            )

            # Use DocumentLoaderFactory to parse content
            from src.document_loader.loader import DocumentLoaderFactory
            chunks_data = await DocumentLoaderFactory.load(
                content=content,
                metadata=metadata,
            )

            if not chunks_data:
                logger.warning(f"No content extracted from document {doc_id}")
                await self._document_repository.update_status(doc_id, DocumentStatus.FAILED)
                return False

            # Extract text from chunks
            chunks = []
            for chunk_data in chunks_data:
                text = chunk_data.get("text", "")
                if text.strip():
                    chunks.append(text.strip())

            if not chunks:
                logger.warning(f"No text chunks generated for document {doc_id}")
                await self._document_repository.update_status(doc_id, DocumentStatus.FAILED)
                return False

            # Further chunk the text if needed
            all_text = "\n\n".join(chunks)
            final_chunks = self._chunk_text(all_text)

            if not final_chunks:
                logger.warning(f"No chunks generated for document {doc_id}")
                await self._document_repository.update_status(doc_id, DocumentStatus.FAILED)
                return False

            # Generate embeddings for chunks
            embeddings = []
            for chunk in final_chunks:
                embedding = await self._embedding.async_embed_query(chunk)
                embeddings.append(embedding)

            # Upsert to vector store
            await self._vector_store.upsert(
                vectors=embeddings,
                texts=final_chunks,
                payloads=[{
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "filename": filename,
                } for i in range(len(final_chunks))],
            )

            # Update status to completed
            await self._document_repository.update(
                doc_id,
                status=DocumentStatus.COMPLETED,
                chunk_count=len(final_chunks),
            )

            # Invalidate related cache entries
            await self._cache.clear()

            logger.info(f"Document ingested: {doc_id} ({len(final_chunks)} chunks)")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest document {doc_id}: {e}")
            await self._document_repository.update_status(doc_id, DocumentStatus.FAILED)
            return False

    async def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        """Get document by ID."""
        return await self._document_repository.get(doc_id)

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DocumentStatus] = None,
    ) -> list[DocumentRecord]:
        """List documents with optional filtering."""
        return await self._document_repository.list(
            skip=skip,
            limit=limit,
            status=status,
        )

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its vectors.

        Args:
            doc_id: Document ID

        Returns:
            True if deletion was successful
        """
        try:
            # Delete from vector store
            await self._vector_store.delete(doc_id)

            # Delete from repository
            await self._document_repository.delete(doc_id)

            # Invalidate cache
            await self._cache.clear(f"doc:{doc_id}:*")

            logger.info(f"Document deleted: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into chunks with overlap."""
        if not text or not text.strip():
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self._chunk_size
            chunk = text[start:end]

            # Try to break at sentence or paragraph boundary
            if end < text_length:
                for sep in ["\n\n", "\n", ". ", " "]:
                    last_sep = chunk.rfind(sep)
                    if last_sep > self._chunk_size // 2:
                        chunk = chunk[:last_sep + len(sep)]
                        end = start + len(chunk)
                        break

            chunks.append(chunk.strip())
            start = end - self._chunk_overlap if end < text_length else text_length

        return [c for c in chunks if c.strip()]
