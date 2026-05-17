"""Document repository port - abstract interface for document metadata storage."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class DocumentStatus(str, Enum):
    """Document processing status."""
    
    PENDING = "pending"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DocumentRecord:
    """
    Immutable document metadata record.
    
    Attributes:
        doc_id: Unique document identifier.
        title: Document title.
        source: Document source/origin.
        filename: Original filename.
        file_size: File size in bytes.
        mime_type: MIME type of the file.
        status: Processing status.
        chunk_size: Chunk size for splitting.
        chunk_overlap: Overlap between chunks.
        chunk_count: Number of chunks created from the document.
        error_message: Error message if failed.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """
    
    doc_id: str
    title: str
    source: str
    filename: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    status: DocumentStatus = DocumentStatus.PENDING
    chunk_size: int = 500
    chunk_overlap: int = 50
    chunk_count: int = 0
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentRepositoryPort(ABC):
    """
    Abstract interface for document metadata storage.
    
    This port defines the contract for storing and retrieving
    document metadata. Implementations can use SQLite, PostgreSQL,
    or any database.
    """
    
    @abstractmethod
    async def add(self, record: DocumentRecord) -> bool:
        """
        Add a new document record.
        
        Args:
            record: The document record to add.
            
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def get(self, doc_id: str) -> DocumentRecord | None:
        """
        Get a document record by ID.
        
        Args:
            doc_id: The document identifier.
            
        Returns:
            The document record, or None if not found.
        """
        pass
    
    @abstractmethod
    async def update(self, doc_id: str, **kwargs: Any) -> bool:
        """
        Update document record fields.
        
        Args:
            doc_id: The document identifier.
            **kwargs: Fields to update.
            
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def update_status(
        self,
        doc_id: str,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> bool:
        """
        Update document processing status.
        
        Args:
            doc_id: The document identifier.
            status: New processing status.
            error_message: Optional error message for failed status.
            
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """
        Delete a document record.
        
        Args:
            doc_id: The document identifier.
            
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: DocumentStatus | None = None,
    ) -> list[DocumentRecord]:
        """
        List document records with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            status: Optional status filter.
            
        Returns:
            List of document records.
        """
        pass
    
    @abstractmethod
    async def count(self, status: DocumentStatus | None = None) -> int:
        """
        Count documents.
        
        Args:
            status: Optional status filter.
            
        Returns:
            Number of documents matching criteria.
        """
        pass
