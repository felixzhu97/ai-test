import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

from src.schemas import (
    DocumentSource,
    DocumentMetadata,
    ChatRequest,
)


class TestSchemas:
    """Test Pydantic schemas."""

    def test_document_metadata(self):
        """Test DocumentMetadata schema."""
        metadata = DocumentMetadata(
            source=DocumentSource.MARKDOWN,
            filename="test.md",
            doc_id="test-123",
        )
        assert metadata.source == DocumentSource.MARKDOWN
        assert metadata.filename == "test.md"
        assert metadata.doc_id == "test-123"

    def test_chat_request_defaults(self):
        """Test ChatRequest default values."""
        request = ChatRequest(query="What is AI?")
        assert request.query == "What is AI?"
        assert request.session_id is None
        assert request.top_k == 5
        assert request.temperature == 0.7

    def test_chat_request_custom_values(self):
        """Test ChatRequest with custom values."""
        request = ChatRequest(
            query="What is RAG?",
            session_id="custom-session",
            top_k=10,
            temperature=0.5,
        )
        assert request.session_id == "custom-session"
        assert request.top_k == 10
        assert request.temperature == 0.5

    def test_chat_request_validation(self):
        """Test ChatRequest validation."""
        with pytest.raises(Exception):
            ChatRequest(query="", top_k=0)

        with pytest.raises(Exception):
            ChatRequest(query="test", temperature=-1)


class TestDocumentLoader:
    """Test document loaders."""

    @pytest.mark.asyncio
    async def test_markdown_loader(self, sample_markdown_bytes):
        """Test MarkdownLoader."""
        from src.document_loader.loader import MarkdownLoader
        from src.schemas import DocumentMetadata, DocumentSource

        metadata = DocumentMetadata(
            source=DocumentSource.MARKDOWN,
            filename="test.md",
        )

        loader = MarkdownLoader()
        chunks = []
        async for chunk in loader.load(sample_markdown_bytes, metadata):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "test" in chunks[0]["text"].lower()
        assert chunks[0]["metadata"]["source"] == "markdown"

    @pytest.mark.asyncio
    async def test_text_loader(self):
        """Test TextLoader."""
        from src.document_loader.loader import TextLoader
        from src.schemas import DocumentMetadata, DocumentSource

        metadata = DocumentMetadata(source=DocumentSource.TEXT)
        content = b"Hello, this is a test document."

        loader = TextLoader()
        chunks = []
        async for chunk in loader.load(content, metadata):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "Hello" in chunks[0]["text"]


class TestIngestionService:
    """Test IngestionService."""

    @pytest.mark.asyncio
    async def test_split_text(self, mock_settings):
        """Test text splitting."""
        with patch("src.services.ingestion.get_embedding_model"), \
             patch("src.services.ingestion.get_vector_store"):
            from src.services.ingestion import IngestionService

            service = IngestionService(chunk_size=50, chunk_overlap=10)

            text = "Hello world " * 20
            chunks = service._split_text(text)

            assert len(chunks) > 1
            assert all(chunk.strip() for chunk in chunks)

    @pytest.mark.asyncio
    async def test_ingest(self, mock_settings, mock_vector_store, mock_embedding_model):
        """Test document ingestion."""
        from src.services.ingestion import IngestionService

        service = IngestionService(
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
        )

        result = await service.ingest(
            text="Test document content",
            metadata={"source": "test"},
            doc_id="test-doc-123",
        )

        assert result["doc_id"] == "test-doc-123"
        assert result["chunks"] >= 1
        mock_vector_store.insert.assert_called_once()


class TestEmbeddingModel:
    """Test EmbeddingModel."""

    def test_embed(self, mock_settings):
        """Test embedding generation."""
        with patch("src.core.embedding.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1] * 384]
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            from src.core.embedding import EmbeddingModel

            model = EmbeddingModel()
            embeddings = model.embed(["test text"])

            assert len(embeddings) == 1
            assert len(embeddings[0]) == 384

    def test_embed_query(self, mock_settings):
        """Test single query embedding."""
        with patch("src.core.embedding.SentenceTransformer") as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1] * 384]
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            from src.core.embedding import EmbeddingModel

            model = EmbeddingModel()
            embedding = model.embed_query("test query")

            assert len(embedding) == 384


class TestVectorStore:
    """Test VectorStore."""

    def test_insert(self, mock_settings, mock_vector_store):
        """Test vector insertion."""
        vectors = [[0.1] * 384, [0.2] * 384]
        texts = ["text1", "text2"]
        metadata = [{"source": "test1"}, {"source": "test2"}]

        ids = mock_vector_store.insert(vectors, texts, metadata)

        assert len(ids) == 3
        mock_vector_store.insert.assert_called_once()

    def test_search(self, mock_vector_store):
        """Test vector search."""
        results = mock_vector_store.search([0.1] * 384, top_k=5)

        assert len(results) == 2
        assert results[0]["distance"] == 0.9
        mock_vector_store.search.assert_called_once()


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_health_endpoint(self, mock_settings):
        """Test health endpoint."""
        with patch("src.main.VectorStore") as mock_vs, \
             patch("src.main.EmbeddingModel") as mock_em:
            mock_vs_instance = MagicMock()
            mock_vs_instance.client = MagicMock()
            mock_vs_instance.collection_name = "test"
            mock_vs.return_value = mock_vs_instance

            mock_em.return_value = MagicMock()

            from src.main import app

            client = TestClient(app)
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "qdrant_connected" in data

    def test_root_endpoint(self, mock_settings):
        """Test root endpoint."""
        with patch("src.main.VectorStore") as mock_vs, \
             patch("src.main.EmbeddingModel") as mock_em:
            mock_vs.return_value = MagicMock()
            mock_em.return_value = MagicMock()

            from src.main import app

            client = TestClient(app)
            response = client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "RAG Service"
            assert "endpoints" in data


class TestLLMGateway:
    """Test LLM Gateway."""

    def test_get_llm_openai(self, mock_settings):
        """Test OpenAI LLM initialization."""
        with patch("src.core.llm_gateway.ChatOpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()

            from src.core.llm_gateway import LLMGateway

            LLMGateway.reset()
            llm = LLMGateway.get_llm(provider="openai", model="gpt-4o-mini")

            mock_openai.assert_called_once()

    def test_get_llm_anthropic(self, mock_settings):
        """Test Anthropic LLM initialization."""
        with patch("src.core.llm_gateway.ChatAnthropic") as mock_anthropic:
            mock_anthropic.return_value = MagicMock()

            from src.core.llm_gateway import LLMGateway

            LLMGateway.reset()
            llm = LLMGateway.get_llm(provider="anthropic", model="claude-3-opus")

            mock_anthropic.assert_called_once()

    def test_get_llm_ollama(self, mock_settings):
        """Test Ollama LLM initialization."""
        with patch("src.core.llm_gateway.ChatOllama") as mock_ollama:
            mock_ollama.return_value = MagicMock()

            from src.core.llm_gateway import LLMGateway

            LLMGateway.reset()
            llm = LLMGateway.get_llm(provider="ollama", model="qwen2.5:7b")

            mock_ollama.assert_called_once()

    def test_get_llm_invalid_provider(self, mock_settings):
        """Test invalid LLM provider."""
        from src.core.llm_gateway import LLMGateway

        LLMGateway.reset()

        with pytest.raises(ValueError):
            LLMGateway.get_llm(provider="invalid")
