"""Chat API endpoints with dependency injection."""

from __future__ import annotations

import uuid
import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from application.dependencies import (
    VectorStoreDep,
    EmbeddingDep,
    LLMDep,
    CacheDep,
    DocumentRepositoryDep,
)
from application.rag_chain_service import RAGChainService
from application.document_service import DocumentService
from schemas import (
    ChatRequest,
    ChatResponse,
    SourceDocument,
    ChatHistoryItem,
)
from domain.ports import Message
from ..persistence.session_store import get_session_store, SessionStore
from ..persistence.session_store import ChatMessage
from config import get_settings


router = APIRouter(prefix="/chat", tags=["Chat"])


def get_rag_chain_service(
    vector_store: VectorStoreDep,
    embedding: EmbeddingDep,
    llm: LLMDep,
    cache: CacheDep,
) -> RAGChainService:
    """Create RAG chain service instance."""
    return RAGChainService(
        vector_store=vector_store,
        embedding=embedding,
        llm=llm,
        cache=cache,
        top_k=5,
    )


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


def get_session_store_dep() -> SessionStore:
    """Get session store instance."""
    return get_session_store()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: Annotated[RAGChainService, Depends(get_rag_chain_service)],
    session_store: Annotated[SessionStore, Depends(get_session_store_dep)],
):
    """Process a chat query and return a response with sources."""
    settings = get_settings()
    session_id = request.session_id or str(uuid.uuid4())

    # Ensure session exists
    session = session_store.get_session(session_id)
    if not session:
        session_store.create_session(session_id)

    try:
        # Get chat history for context
        history_messages = session_store.get_messages(session_id)
        chat_history = [
            Message(role=msg.role, content=msg.content)
            for msg in history_messages
        ]

        # Process query
        answer, sources = await rag_service.chat(
            query=request.query,
            session_id=session_id,
            doc_ids=request.doc_ids,
            chat_history=chat_history,
            temperature=request.temperature,
        )

        # Persist messages
        session_store.add_message(
            session_id=session_id,
            role="user",
            content=request.query,
        )
        session_store.add_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=[s.model_dump() for s in sources],
        )

        logger.info(f"Chat session {session_id}: query processed successfully")

        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
            model=settings.LLM_MODEL,
            processing_time_ms=0.0,
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    rag_service: Annotated[RAGChainService, Depends(get_rag_chain_service)],
    session_store: Annotated[SessionStore, Depends(get_session_store_dep)],
):
    """Stream a chat response token by token."""
    settings = get_settings()
    session_id = request.session_id or str(uuid.uuid4())

    # Ensure session exists
    session = session_store.get_session(session_id)
    if not session:
        session_store.create_session(session_id)

    try:
        # Get chat history for context
        history_messages = session_store.get_messages(session_id)
        chat_history = [
            Message(role=msg.role, content=msg.content)
            for msg in history_messages
        ]

        full_response = []
        sources = []

        async def generate():
            nonlocal sources
            try:
                async for chunk in rag_service.stream_chat(
                    query=request.query,
                    session_id=session_id,
                    doc_ids=request.doc_ids,
                    chat_history=chat_history,
                    temperature=request.temperature,
                ):
                    full_response.append(chunk)
                    yield f"data: {chunk.replace(chr(10), '<br>')}\n\n"

            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: Error: {str(e)}\n\n"

            # Send end markers
            yield f"data: [DONE]\n\n"
            yield f"event: meta\n"
            yield f"data: {json.dumps({'model': settings.LLM_MODEL})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-Id": session_id,
            },
        )

    except Exception as e:
        logger.error(f"Error in stream chat: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stream response: {str(e)}")


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    session_store: Annotated[SessionStore, Depends(get_session_store_dep)],
):
    """Get chat history for a session."""
    messages = session_store.get_messages(session_id)

    if not messages:
        return {"session_id": session_id, "messages": [], "total": 0}

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "sources": json.loads(msg.sources) if msg.sources else [],
            }
            for msg in messages
        ],
        "total": len(messages),
    }


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    session_store: Annotated[SessionStore, Depends(get_session_store_dep)],
):
    """Clear chat history for a session."""
    success = session_store.delete_session(session_id)
    if success:
        return {"status": "success", "message": f"History for session {session_id} cleared"}
    return {"status": "error", "message": "Failed to clear history"}


@router.post("/ingest-text")
async def ingest_text(
    text: str = Query(..., description="Text to ingest"),
    title: str = Query("Text Document", description="Document title"),
    doc_service: Annotated[DocumentService, Depends(get_document_service)] = None,
    rag_service: Annotated[RAGChainService, Depends(get_rag_chain_service)] = None,
):
    """Ingest raw text as a document."""
    doc_id = str(uuid.uuid4())

    try:
        content = text.encode("utf-8")

        if doc_service:
            # Use new document service
            doc_record = await doc_service.upload_document(
                content=content,
                filename=title,
                title=title,
                source_type="text",
            )

            success = await doc_service.ingest_document(
                doc_id=doc_record.doc_id,
                content=content,
                filename=title,
            )

            return {
                "doc_id": doc_record.doc_id,
                "title": title,
                "status": "success" if success else "failed",
            }
        else:
            # Fallback to original implementation
            from src.document_loader.loader import DocumentLoaderFactory
            from src.schemas import DocumentMetadata, DocumentSource

            metadata = DocumentMetadata(
                source=DocumentSource.TEXT,
                title=title,
                doc_id=doc_id,
            )

            chunks = await DocumentLoaderFactory.load(
                content=content,
                metadata=metadata,
            )

            from src.services.ingestion import IngestionService
            ingestion_service = IngestionService()
            full_text = "\n\n".join(chunk["text"] for chunk in chunks)

            result = await ingestion_service.ingest(
                text=full_text,
                metadata=metadata.model_dump(exclude_none=True),
                doc_id=doc_id,
            )

            logger.info(f"Ingested text {doc_id}: {title} with {result['chunks']} chunks")

            return {
                "doc_id": doc_id,
                "title": title,
                "chunks": result["chunks"],
                "status": "success",
            }

    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest text: {str(e)}")
