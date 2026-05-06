from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from loguru import logger
from ..core.embedding import EmbeddingModel, get_embedding_model
from ..core.vector_store import VectorStore, get_vector_store
from ..core.llm_gateway import get_llm
from ..schemas import ChatRequest, ChatResponse, SourceDocument
from ..config import get_settings


SYSTEM_PROMPT = """你是一个专业的AI助手。请根据以下上下文信息回答用户的问题。

上下文信息:
{context}

用户问题: {question}

请基于上下文信息给出准确、详细的回答。如果上下文中没有相关信息，请明确告知用户。
"""

FALLBACK_PROMPT = """你是一个专业的AI助手。请回答用户的问题。

用户问题: {question}

请给出准确、详细的回答。
"""


class RAGChain:
    """RAG chain for question answering with context retrieval."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_model: Optional[EmbeddingModel] = None,
        llm: Optional[BaseChatModel] = None,
        top_k: int = 5,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_model = embedding_model or get_embedding_model()
        self.llm = llm
        self.top_k = top_k

        self.prompt_template = PromptTemplate(
            template=SYSTEM_PROMPT,
            input_variables=["context", "question"],
        )

        self.fallback_template = PromptTemplate(
            template=FALLBACK_PROMPT,
            input_variables=["question"],
        )

    def _get_llm(self, temperature: float = 0.7) -> BaseChatModel:
        """Get LLM instance with specified temperature."""
        if self.llm is None:
            return get_llm(temperature=temperature)
        return self.llm

    async def query(self, request: ChatRequest) -> ChatResponse:
        """Process a query and return a response with sources."""
        import time
        start = time.perf_counter()

        query_vector = self.embedding_model.embed_query(request.query)

        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=request.top_k,
            doc_ids=request.doc_ids,
        )

        sources = [
            SourceDocument(
                text=r["text"],
                score=r["distance"],
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

        if results:
            context = "\n\n".join(
                f"[来源 {i+1}] {r['text']}" for i, r in enumerate(results)
            )
            prompt = self.prompt_template.format(
                context=context,
                question=request.query,
            )
        else:
            prompt = self.fallback_template.format(question=request.query)

        llm = self._get_llm(temperature=request.temperature)

        if hasattr(llm, "ainvoke"):
            response = await llm.ainvoke(prompt)
            answer = response.content if hasattr(response, "content") else str(response)
        elif hasattr(llm, "apredict"):
            answer = await llm.apredict(prompt)
        else:
            answer = llm.invoke(prompt)
            if hasattr(answer, "content"):
                answer = answer.content

        processing_time = (time.perf_counter() - start) * 1000

        settings = get_settings()
        current_model = settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.LLM_MODEL
        session_id = request.session_id or "default"
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
            model=current_model,
            processing_time_ms=processing_time,
        )

    async def stream_query(self, request: ChatRequest):
        """Stream query response token by token."""
        import time
        start = time.perf_counter()

        query_vector = self.embedding_model.embed_query(request.query)

        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=request.top_k,
            doc_ids=request.doc_ids,
        )

        sources = [
            SourceDocument(
                text=r["text"],
                score=r["distance"],
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

        if results:
            context = "\n\n".join(
                f"[来源 {i+1}] {r['text']}" for i, r in enumerate(results)
            )
            prompt = self.prompt_template.format(
                context=context,
                question=request.query,
            )
        else:
            prompt = self.fallback_template.format(question=request.query)

        llm = self._get_llm(temperature=request.temperature)

        if hasattr(llm, "astream"):
            async for chunk in llm.astream(prompt):
                yield chunk.content if hasattr(chunk, "content") else str(chunk)
        elif hasattr(llm, "stream"):
            for chunk in llm.stream(prompt):
                yield chunk.content if hasattr(chunk, "content") else str(chunk)
        else:
            response = llm.invoke(prompt)
            yield response.content if hasattr(response, "content") else str(response)
