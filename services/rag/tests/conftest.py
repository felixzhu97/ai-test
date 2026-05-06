import pytest
import asyncio
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("src.config.get_settings") as mock:
        settings = MagicMock()
        settings.QDRANT_HOST = "localhost"
        settings.QDRANT_PORT = 6333
        settings.QDRANT_COLLECTION = "test_docs"
        settings.QDRANT_VECTOR_DIM = 384
        settings.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        settings.EMBEDDING_DEVICE = "cpu"
        settings.LLM_PROVIDER = "openai"
        settings.LLM_MODEL = "gpt-4o-mini"
        settings.CHUNK_SIZE = 500
        settings.CHUNK_OVERLAP = 50
        settings.MAX_FILE_SIZE = 10 * 1024 * 1024
        mock.return_value = settings
        yield settings


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    store = MagicMock()
    store.insert.return_value = [1, 2, 3]
    store.search.return_value = [
        {"id": 1, "distance": 0.9, "text": "Test content", "metadata": {}},
        {"id": 2, "distance": 0.8, "text": "More content", "metadata": {}},
    ]
    store.get_stats.return_value = {"total_vectors": 100}
    return store


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for testing."""
    model = MagicMock()
    model.embed.return_value = [[0.1] * 384]
    model.embed_query.return_value = [0.1] * 384
    model.dimension = 384
    return model


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    # Test Document

    This is a test document for RAG processing.

    ## Section 1
    Some content here.

    ## Section 2
    More content here.
    """


@pytest.fixture
def sample_markdown_bytes():
    """Sample markdown content as bytes."""
    return b"""# Test Document

This is a test document for RAG processing.

## Section 1
Some content here.

## Section 2
More content here.
"""


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF-like content (minimal)."""
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\ntest content"
