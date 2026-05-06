import uuid
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional
from loguru import logger
from ..schemas import (
    UploadResponse,
    DocumentListResponse,
    DocumentStats,
    DocumentMetadata,
    DocumentSource,
)
from ..document_loader.loader import DocumentLoaderFactory, load_from_url
from ..services.ingestion import IngestionService
from ..core.vector_store import get_vector_store
from ..config import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])

_document_registry: dict[str, dict] = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    collection: Optional[str] = None,
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

    doc_id = str(uuid.uuid4())
    metadata = DocumentMetadata(
        source=source,
        filename=filename,
        title=title or filename,
        doc_id=doc_id,
    )

    try:
        chunks = await DocumentLoaderFactory.load(content=content, metadata=metadata)

        if not chunks:
            raise HTTPException(status_code=400, detail="No content could be extracted from the file")

        ingestion_service = IngestionService()
        full_text = "\n\n".join(chunk["text"] for chunk in chunks)

        result = await ingestion_service.ingest(
            text=full_text,
            metadata=metadata.model_dump(exclude_none=True),
            doc_id=doc_id,
        )

        _document_registry[doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "source": source.value,
            "chunks": result["chunks"],
            "uploaded_at": time.time(),
            "metadata": metadata.model_dump(exclude_none=True),
        }

        logger.info(f"Uploaded document {doc_id}: {filename} with {result['chunks']} chunks")

        return UploadResponse(
            doc_id=doc_id,
            filename=filename,
            chunks=result["chunks"],
            status="success",
        )

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/ingest-url")
async def ingest_url(
    url: str = Query(..., description="URL to ingest"),
    title: Optional[str] = Query(None, description="Document title"),
):
    """Ingest a document from a URL."""
    doc_id = str(uuid.uuid4())

    metadata = DocumentMetadata(
        source=DocumentSource.WEB,
        url=url,
        title=title or url,
        doc_id=doc_id,
    )

    try:
        chunks = await load_from_url(url=url, metadata=metadata)

        if not chunks:
            raise HTTPException(status_code=400, detail="No content could be extracted from the URL")

        ingestion_service = IngestionService()
        full_text = "\n\n".join(chunk["text"] for chunk in chunks)

        result = await ingestion_service.ingest(
            text=full_text,
            metadata=metadata.model_dump(exclude_none=True),
            doc_id=doc_id,
        )

        _document_registry[doc_id] = {
            "doc_id": doc_id,
            "filename": url,
            "source": DocumentSource.WEB.value,
            "chunks": result["chunks"],
            "uploaded_at": time.time(),
            "metadata": metadata.model_dump(exclude_none=True),
        }

        logger.info(f"Ingested URL {doc_id}: {url} with {result['chunks']} chunks")

        return UploadResponse(
            doc_id=doc_id,
            filename=url,
            chunks=result["chunks"],
            status="success",
        )

    except Exception as e:
        logger.error(f"Error ingesting URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest URL: {str(e)}")


@router.get("/database", response_model=DocumentListResponse)
async def list_documents_from_database():
    """List all documents stored in the vector database."""
    try:
        vector_store = get_vector_store()
        docs = vector_store.get_all_documents()
        
        documents = [
            DocumentStats(
                doc_id=doc["doc_id"],
                filename=doc.get("filename", "Unknown"),
                total_chunks=0,
                source=doc.get("source", "unknown"),
            )
            for doc in docs
        ]
        
        return DocumentListResponse(documents=documents, total=len(documents))
    except Exception as e:
        logger.error(f"Error listing documents from database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(collection: Optional[str] = None):
    """List all uploaded documents."""
    documents = [
        DocumentStats(
            doc_id=doc["doc_id"],
            filename=doc["filename"],
            total_chunks=doc["chunks"],
            source=doc["source"],
            uploaded_at=doc.get("uploaded_at"),
        )
        for doc in _document_registry.values()
    ]

    return DocumentListResponse(documents=documents, total=len(documents))


@router.get("/{doc_id}/stats")
async def get_document_stats(doc_id: str):
    """Get statistics for a specific document."""
    if doc_id not in _document_registry:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = _document_registry[doc_id]
    vector_store = get_vector_store()

    return {
        "doc_id": doc_id,
        "filename": doc["filename"],
        "total_chunks": doc["chunks"],
        "source": doc["source"],
        "uploaded_at": doc.get("uploaded_at"),
        "vector_stats": vector_store.get_stats(),
    }


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its associated vectors."""
    if doc_id not in _document_registry:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        vector_store = get_vector_store()
        vector_store.delete_by_doc_id(doc_id)

        del _document_registry[doc_id]

        logger.info(f"Deleted document: {doc_id}")

        return {"status": "success", "message": f"Document {doc_id} deleted"}

    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
