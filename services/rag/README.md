# RAG Service

Production-grade RAG (Retrieval-Augmented Generation) service with Qdrant vector store.

## Features

- **Multi-format Document Support**: Markdown, PDF, Web pages, Plain text
- **Vector Search**: Qdrant-powered semantic search
- **Flexible LLM Support**: OpenAI GPT, Anthropic Claude, Ollama (local)
- **Streaming Responses**: Real-time token streaming
- **Conversation History**: Session-based chat history
- **Docker Ready**: One-click deployment with Qdrant

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    RAG Service                      │
│                     Port 8001                        │
├─────────────────────────────────────────────────────┤
│  API Layer                                          │
│  ├── /documents (upload, list, delete, stats)      │
│  └── /chat (query, stream, history)                │
├─────────────────────────────────────────────────────┤
│  Core Components                                    │
│  ├── LLM Gateway (OpenAI/Claude/Ollama)           │
│  ├── Embedding Model (Sentence Transformers)      │
│  └── Vector Store (Qdrant)                        │
├─────────────────────────────────────────────────────┤
│  Document Processing                                │
│  ├── Document Loaders (PDF, MD, Web, Text)        │
│  └── Ingestion Service (chunking, embedding)      │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  Qdrant Vector DB   │
         │     Port 6333       │
         └─────────────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
cd services/rag

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Configuration

```bash
cp .env.example .env

# Edit .env with your settings
vim .env
```

Required environment variables:

```env
# Qdrant (if not using Docker)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM Provider
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key

# Or for Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

### 3. Start Qdrant (with Docker)

```bash
docker compose up qdrant -d
```

### 4. Run the Service

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Verify

```bash
curl http://localhost:8001/health
```

## API Reference

### Document Management

#### Upload Document

```bash
curl -X POST http://localhost:8001/documents/upload \
  -F "file=@document.pdf" \
  -F "title=My Document"
```

#### Ingest from URL

```bash
curl -X POST "http://localhost:8001/documents/ingest-url?url=https://example.com&title=Example"
```

#### List Documents

```bash
curl http://localhost:8001/documents/
```

#### Delete Document

```bash
curl -X DELETE http://localhost:8001/documents/{doc_id}
```

### Chat

#### Query

```bash
curl -X POST http://localhost:8001/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the documents?",
    "session_id": "my-session",
    "top_k": 5
  }'
```

#### Stream Response

```bash
curl -X POST http://localhost:8001/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain RAG", "session_id": "stream-test"}'
```

#### Get Chat History

```bash
curl http://localhost:8001/chat/history/my-session
```

### Ingest Text Directly

```bash
curl -X POST "http://localhost:8001/chat/ingest-text?text=Hello%20World&title=Test"
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Service host |
| `PORT` | 8001 | Service port |
| `QDRANT_HOST` | localhost | Qdrant server host |
| `QDRANT_PORT` | 6333 | Qdrant server port |
| `COLLECTION_NAME` | ai_test_docs | Vector collection name |
| `VECTOR_DIM` | 384 | Embedding dimension |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer model |
| `EMBEDDING_DEVICE` | cuda | cuda or cpu |
| `LLM_PROVIDER` | openai | openai, anthropic, or ollama |
| `LLM_MODEL` | gpt-4o-mini | Model name |
| `CHUNK_SIZE` | 500 | Text chunk size (tokens) |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |

## Docker Deployment

### Full Stack (RAG + Qdrant)

```bash
docker compose up -d
```

### RAG Only (external Qdrant)

```bash
docker build -t rag-service .
docker run -p 8001:8001 \
  -e QDRANT_HOST=your-qdrant-host \
  -e OPENAI_API_KEY=your-key \
  rag-service
```

## Development

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Project Structure

```
services/rag/
├── src/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings management
│   ├── schemas.py           # Pydantic models
│   ├── api/
│   │   ├── documents.py     # Document API routes
│   │   └── chat.py          # Chat API routes
│   ├── core/
│   │   ├── llm_gateway.py   # LLM provider abstraction
│   │   ├── embedding.py    # Embedding model
│   │   └── vector_store.py  # Qdrant integration
│   ├── document_loader/
│   │   └── loader.py       # Document loaders
│   └── services/
│       ├── ingestion.py    # Document ingestion
│       └── rag_chain.py    # RAG chain logic
├── tests/
│   ├── conftest.py         # Test fixtures
│   └── test_rag_api.py    # Unit tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Supported Document Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Markdown | .md, .markdown | Converted to plain text |
| PDF | .pdf | Text extraction |
| Web | URL | HTML parsing |
| Plain Text | .txt | Direct processing |

## License

MIT
