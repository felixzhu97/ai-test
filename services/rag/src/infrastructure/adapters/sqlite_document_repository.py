"""SQLite document repository adapter - implements DocumentRepositoryPort interface."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from domain.ports.document_repository import (
    DocumentRepositoryPort,
    DocumentRecord,
    DocumentStatus,
)


def _get_document_store():
    """Lazy import document store to avoid circular imports."""
    from src.persistence.document_metadata import DocumentMetadataStore
    return DocumentMetadataStore()


class SQLiteDocumentRepositoryAdapter(DocumentRepositoryPort):
    """SQLite document repository adapter implementing DocumentRepositoryPort interface."""

    def __init__(self, store=None) -> None:
        self._store = store or _get_document_store()

    def _to_record(self, stored) -> DocumentRecord:
        """Convert storage record to domain model."""
        return DocumentRecord(
            doc_id=stored.doc_id,
            title=stored.title,
            source=stored.source,
            filename=stored.filename,
            file_size=stored.file_size,
            mime_type=stored.mime_type,
            status=DocumentStatus(stored.status),
            chunk_size=stored.chunk_size,
            chunk_overlap=stored.chunk_overlap,
            chunk_count=getattr(stored, 'chunk_count', 0),
            error_message=stored.error_message,
            created_at=datetime.fromisoformat(stored.created_at) if stored.created_at else None,
            updated_at=datetime.fromisoformat(stored.updated_at) if stored.updated_at else None,
        )

    def _to_stored(self, record: DocumentRecord):
        """Convert domain model to storage record."""
        from src.persistence.document_metadata import DocumentRecord as StoredRecord
        
        return StoredRecord(
            doc_id=record.doc_id,
            title=record.title,
            source=record.source,
            filename=record.filename,
            file_size=record.file_size,
            mime_type=record.mime_type,
            chunk_count=0,
            chunk_size=record.chunk_size,
            chunk_overlap=record.chunk_overlap,
            status=record.status.value if isinstance(record.status, DocumentStatus) else record.status,
            error_message=record.error_message,
            created_at=record.created_at.isoformat() if record.created_at else datetime.now().isoformat(),
            updated_at=record.updated_at.isoformat() if record.updated_at else datetime.now().isoformat(),
        )

    async def add(self, record: DocumentRecord) -> bool:
        """Add a new document record."""
        stored = self._to_stored(record)
        return self._store.add_document(stored)

    async def get(self, doc_id: str) -> Optional[DocumentRecord]:
        """Get a document record by ID."""
        stored = self._store.get_document(doc_id)
        return self._to_record(stored) if stored else None

    async def update(self, doc_id: str, **kwargs: Any) -> bool:
        """Update document record fields."""
        update_kwargs = {}
        if "status" in kwargs:
            status = kwargs["status"]
            update_kwargs["status"] = status.value if isinstance(status, DocumentStatus) else status
        if "error_message" in kwargs:
            update_kwargs["error_message"] = kwargs["error_message"]
        if "chunk_count" in kwargs:
            update_kwargs["chunk_count"] = kwargs["chunk_count"]

        if update_kwargs:
            return self._store.update_document(doc_id=doc_id, **update_kwargs)
        return True

    async def update_status(
        self,
        doc_id: str,
        status: DocumentStatus,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update document processing status."""
        return self._store.update_document(
            doc_id=doc_id,
            status=status.value if isinstance(status, DocumentStatus) else status,
            error_message=error_message,
        )

    async def delete(self, doc_id: str) -> bool:
        """Delete a document record."""
        return self._store.delete_document(doc_id)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DocumentStatus] = None,
    ) -> list[DocumentRecord]:
        """List document records with pagination."""
        stored_list = self._store.list_documents(
            status=status.value if status else None,
            limit=limit,
            offset=skip,
        )
        return [self._to_record(s) for s in stored_list]

    async def count(self, status: Optional[DocumentStatus] = None) -> int:
        """Count documents."""
        docs = self._store.list_documents(
            status=status.value if status else None,
            limit=10000,
            offset=0,
        )
        return len(docs)
