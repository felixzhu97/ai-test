"""Document management API endpoints with dependency injection."""

from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from loguru import logger

from application.dependencies import (
    VectorStoreDep,
    EmbeddingDep,
    CacheDep,
    DocumentRepositoryDep,
)
from application.document_service import DocumentService
from domain.ports import DocumentStatus
from schemas import (
    UploadResponse,
    DocumentListResponse,
    DocumentStats,
    DocumentMetadata,
    DocumentSource,
)
from ..config import get_settings
from ..persistence.document_metadata import get_document_store, DocumentRecord


router = APIRouter(prefix="/documents", tags=["Documents"])


def get_document_service(
    document_repository: DocumentRepositoryDep,
    vector_store: VectorStoreDep,
    embedding: EmbeddingDep,
    cache: CacheDep,
) -> DocumentService:
    """Create document service instance."""
    return DocumentService(
        document_repository=document_repository,
        vector_store=vector_store,
        embedding=embedding,
        cache=cache,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Upload and ingest a document."""
    settings = get_settings()

    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB",
        )

    filename = file.filename or "unknown"
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    source_map = {
        "md": DocumentSource.MARKDOWN,
        "markdown": DocumentSource.MARKDOWN,
        "pdf": DocumentSource.PDF,
        "txt": DocumentSource.TEXT,
        "text": DocumentSource.TEXT,
    }
    source = source_map.get(ext, DocumentSource.TEXT)

    if doc_service:
        # Use new document service
        doc_record = await doc_service.upload_document(
            content=content,
            filename=filename,
            title=title or filename,
            source_type=source.value,
        )

        # Auto-ingest
        success = await doc_service.ingest_document(
            doc_id=doc_record.doc_id,
            content=content,
            filename=filename,
        )

        # Get chunk count from document record
        doc = await doc_service.get_document(doc_record.doc_id)
        chunk_count = doc.chunk_count if doc else 0

        return UploadResponse(
            doc_id=doc_record.doc_id,
            filename=filename,
            chunks=chunk_count,
            status="success" if success else "failed",
        )
    else:
        # Fallback to original implementation
        doc_store = get_document_store()
        doc_id = str(uuid.uuid4())
        metadata = DocumentMetadata(
            source=source,
            filename=filename,
            title=title or filename,
            doc_id=doc_id,
        )

        # Create document record
        record = DocumentRecord(
            doc_id=doc_id,
            title=title or filename,
            source=source.value,
            filename=filename,
            file_size=len(content),
            mime_type=file.content_type,
            status="pending",
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        doc_store.add_document(record)

        try:
            from src.document_loader.loader import DocumentLoaderFactory
            from src.services.ingestion import IngestionService

            chunks = await DocumentLoaderFactory.load(content=content, metadata=metadata)

            if not chunks:
                doc_store.update_document(doc_id=doc_id, status="failed", error_message="No content extracted")
                raise HTTPException(status_code=400, detail="No content could be extracted from the file")

            ingestion_service = IngestionService()
            full_text = "\n\n".join(chunk["text"] for chunk in chunks)

            result = await ingestion_service.ingest(
                text=full_text,
                metadata=metadata.model_dump(exclude_none=True),
                doc_id=doc_id,
            )

            logger.info(f"Uploaded document {doc_id}: {filename} with {result['chunks']} chunks")

            return UploadResponse(
                doc_id=doc_id,
                filename=filename,
                chunks=result["chunks"],
                status="success",
            )

        except Exception as e:
            doc_store.update_document(doc_id=doc_id, status="failed", error_message=str(e))
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/ingest-url")
async def ingest_url(
    url: str = Query(..., description="URL to ingest"),
    title: Optional[str] = Query(None, description="Document title"),
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Ingest a document from a URL."""
    doc_store = get_document_store()
    doc_id = str(uuid.uuid4())

    metadata = DocumentMetadata(
        source=DocumentSource.WEB,
        url=url,
        title=title or url,
        doc_id=doc_id,
    )

    # Create document record
    record = DocumentRecord(
        doc_id=doc_id,
        title=title or url,
        source=DocumentSource.WEB.value,
        status="pending",
    )
    doc_store.add_document(record)

    try:
        from src.document_loader.loader import load_from_url
        from src.services.ingestion import IngestionService

        chunks = await load_from_url(url=url, metadata=metadata)

        if not chunks:
            doc_store.update_document(doc_id=doc_id, status="failed", error_message="No content extracted")
            raise HTTPException(status_code=400, detail="No content could be extracted from the URL")

        ingestion_service = IngestionService()
        full_text = "\n\n".join(chunk["text"] for chunk in chunks)

        result = await ingestion_service.ingest(
            text=full_text,
            metadata=metadata.model_dump(exclude_none=True),
            doc_id=doc_id,
        )

        logger.info(f"Ingested URL {doc_id}: {url} with {result['chunks']} chunks")

        return UploadResponse(
            doc_id=doc_id,
            filename=url,
            chunks=result["chunks"],
            status="success",
        )

    except Exception as e:
        doc_store.update_document(doc_id=doc_id, status="failed", error_message=str(e))
        logger.error(f"Error ingesting URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest URL: {str(e)}")


@router.get("/database", response_model=DocumentListResponse)
async def list_documents_from_database(
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """List all documents stored in the vector database."""
    if doc_service:
        # Use new document service
        status_filter = DocumentStatus(status) if status else None
        documents = await doc_service.list_documents(
            skip=skip,
            limit=limit,
            status=status_filter,
        )

        return DocumentListResponse(
            documents=[
                DocumentStats(
                    doc_id=doc.doc_id,
                    filename=doc.filename or doc.title,
                    total_chunks=doc.chunk_count or 0,
                    source=doc.source,
                    uploaded_at=doc.created_at,
                )
                for doc in documents
            ],
            total=len(documents),
        )
    else:
        # Fallback to original implementation
        doc_store = get_document_store()

        try:
            doc_records = doc_store.list_documents(limit=limit)

            documents = [
                DocumentStats(
                    doc_id=doc.doc_id,
                    filename=doc.filename or doc.title,
                    total_chunks=doc.chunk_count,
                    source=doc.source,
                    uploaded_at=doc.created_at,
                )
                for doc in doc_records
            ]

            return DocumentListResponse(documents=documents, total=len(documents))
        except Exception as e:
            logger.error(f"Error listing documents from database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/")
async def list_documents(
    collection: Optional[str] = None,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """List all uploaded documents from persistent store."""
    if doc_service:
        documents = await doc_service.list_documents(limit=100)
        return {
            "documents": [
                {
                    "doc_id": doc.doc_id,
                    "filename": doc.filename or doc.title,
                    "total_chunks": doc.chunk_count or 0,
                    "source": doc.source,
                }
                for doc in documents
            ],
            "total": len(documents),
        }
    else:
        doc_store = get_document_store()
        doc_records = doc_store.list_documents(limit=100)

        documents = [
            DocumentStats(
                doc_id=doc.doc_id,
                filename=doc.filename or doc.title,
                total_chunks=doc.chunk_count,
                source=doc.source,
                uploaded_at=doc.created_at,
            )
            for doc in doc_records
        ]

        return {"documents": documents, "total": len(documents)}


@router.get("/{doc_id}/stats")
async def get_document_stats(
    doc_id: str,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Get statistics for a specific document."""
    if doc_service:
        doc = await doc_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "doc_id": doc_id,
            "filename": doc.filename or doc.title,
            "title": doc.title,
            "total_chunks": doc.chunk_count or 0,
            "source": doc.source,
            "status": doc.status.value if hasattr(doc.status, 'value') else doc.status,
            "created_at": doc.created_at,
            "file_size": doc.file_size,
        }
    else:
        doc_store = get_document_store()
        doc = doc_store.get_document(doc_id)

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        from src.core.vector_store import get_vector_store
        vector_store = get_vector_store()

        return {
            "doc_id": doc_id,
            "filename": doc.filename or doc.title,
            "title": doc.title,
            "total_chunks": doc.chunk_count,
            "source": doc.source,
            "status": doc.status,
            "created_at": doc.created_at,
            "indexed_at": doc.indexed_at,
            "file_size": doc.file_size,
            "vector_stats": vector_store.get_stats(),
        }


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Delete a document and its associated vectors."""
    if doc_service:
        doc = await doc_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        success = await doc_service.delete_document(doc_id)
        if success:
            return {"status": "success", "message": f"Document {doc_id} deleted"}
        raise HTTPException(status_code=500, detail="Failed to delete document")
    else:
        # Fallback to original implementation
        doc_store = get_document_store()
        doc = doc_store.get_document(doc_id)

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        try:
            from src.core.vector_store import get_vector_store
            vector_store = get_vector_store()
            vector_store.delete_by_doc_id(doc_id)

            doc_store.delete_document(doc_id)

            logger.info(f"Deleted document: {doc_id}")

            return {"status": "success", "message": f"Document {doc_id} deleted"}

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.post("/reindex/{doc_id}")
async def reindex_document(
    doc_id: str,
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Re-index a document in the vector store."""
    if doc_service:
        doc = await doc_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Note: This requires re-uploading the file content
        # For now, just return a message
        return {"status": "info", "message": "Please re-upload the document to re-index"}
    else:
        raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/cleanup-all")
async def cleanup_all_documents(
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
):
    """Clean up all documents and re-index. Use with caution!"""
    if not doc_service:
        raise HTTPException(status_code=501, detail="Service not available")

    # Get all documents
    documents = await doc_service.list_documents(limit=1000)

    # Delete all documents
    deleted_count = 0
    for doc in documents:
        try:
            await doc_service.delete_document(doc.doc_id)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete document {doc.doc_id}: {e}")

    return {
        "status": "success",
        "message": f"Deleted {deleted_count} documents",
        "deleted_count": deleted_count,
    }
