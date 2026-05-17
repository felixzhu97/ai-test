# API Reference

REST API documentation for the AI-Test Platform services.

---

## Table of Contents

- [Text Service (Port 8006)](#text-service-port-8006)
- [TTS Service (Port 8005)](#tts-service-port-8005)
- [RAG Service (Port 8010)](#rag-service-port-8010)
- [Media Generation Service (Port 8015)](#media-generation-service-port-8015)
- [Error Responses](#error-responses)
- [Environment Variables](#environment-variables)

---

## Text Service (Port 8006)

Base URL: `http://localhost:8006`

Text-to-Text LLM service with multi-provider support (OpenAI, Anthropic, Ollama).

### Endpoints Overview

| Method   | Endpoint                    | Description            |
| -------- | --------------------------- | ---------------------- |
| `GET`    | `/api/text/health`          | Health check           |
| `GET`    | `/api/text/providers`       | List LLM providers     |
| `GET`    | `/api/text/models`          | List available models |
| `POST`   | `/api/text/complete`        | Text completion        |
| `POST`   | `/api/text/complete/stream` | Stream completion      |
| `POST`   | `/api/text/chat`            | Chat completion        |
| `POST`   | `/api/text/chat/stream`     | Stream chat completion |
| `GET`    | `/api/text/session/{id}`    | Get session history    |
| `DELETE` | `/api/text/session/{id}`    | Clear session          |
| `POST`   | `/api/text/reset`           | Reset LLM cache        |

---

### Health Check

#### `GET /api/text/health`

**Response:**

```json
{
  "status": "ok",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "version": "0.2.0"
}
```

---

### List Providers

#### `GET /api/text/providers`

**Response:**

```json
[
  {
    "name": "openai",
    "display_name": "OpenAI",
    "models": ["gpt-4o", "gpt-4o-mini"],
    "status": "available"
  },
  {
    "name": "anthropic",
    "display_name": "Anthropic Claude",
    "models": ["claude-sonnet-4-20250514"],
    "status": "configured"
  },
  {
    "name": "ollama",
    "display_name": "Ollama (Local)",
    "models": ["qwen2.5:7b", "llama3.2"],
    "status": "available"
  }
]
```

---

### Text Completion

#### `POST /api/text/complete`

**Request:**

```json
{
  "prompt": "Explain quantum computing:",
  "system_prompt": "You are a helpful assistant.",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**

```json
{
  "text": "Quantum computing is a type of computation...",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "usage": {"latency_ms": 1234},
  "finish_reason": "stop"
}
```

---

### Chat Completion

#### `POST /api/text/chat`

**Request:**

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "session_id": "optional-session-id",
  "provider": "openai",
  "temperature": 0.7
}
```

**Response:**

```json
{
  "text": "I'm doing well, thank you!",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "session_id": "session-uuid",
  "usage": {"latency_ms": 567, "history_length": 3},
  "finish_reason": "stop"
}
```

---

## TTS Service (Port 8005)

Base URL: `http://localhost:8005`

Text-to-Speech service with multiple provider support (Edge, Azure, Google, ElevenLabs, Coqui).

### Endpoints Overview

| Method | Endpoint          | Description             |
| ------ | ----------------- | ----------------------- |
| `GET`  | `/tts/health`     | Health check            |
| `GET`  | `/tts/voices`     | List available voices  |
| `GET`  | `/tts/providers`   | List TTS providers      |
| `GET`  | `/tts/provider`   | Get current provider    |
| `POST` | `/tts/synthesize` | Synthesize speech       |
| `POST` | `/tts/stream`     | Stream speech           |

---

### Health Check

#### `GET /tts/health`

**Response:**

```json
{
  "status": "ok",
  "provider": "edge",
  "provider_status": "available",
  "version": "0.2.0",
  "components": {}
}
```

---

### List Voices

#### `GET /tts/voices`

**Query Parameters:**

| Parameter | Type   | Description          |
| --------- | ------ | -------------------- |
| `language` | string | Filter by language   |

**Response:**

```json
[
  {"voice_id": "en-US-JennyNeural", "name": "Jenny", "language": "en-US"},
  {"voice_id": "en-GB-SoniaNeural", "name": "Sonia", "language": "en-GB"},
  {"voice_id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao", "language": "zh-CN"}
]
```

---

### Synthesize Speech

#### `POST /tts/synthesize`

**Request:**

```json
{
  "text": "Hello, world!",
  "voice": "en-US-JennyNeural",
  "language": "en-US",
  "speed": 1.0,
  "pitch": 0,
  "output_format": "mp3"
}
```

**Response:** Audio binary (mp3/wav/ogg/flac)

---

## RAG Service (Port 8010)

Base URL: `http://localhost:8010`

Retrieval-augmented generation with Qdrant vector store.

### Endpoints Overview

| Method   | Endpoint                     | Description                   |
| -------- | ---------------------------- | ----------------------------- |
| `GET`    | `/health`                    | Health check                  |
| `POST`   | `/documents/upload`          | Upload document               |
| `POST`   | `/documents/ingest-url`      | Ingest from URL               |
| `GET`    | `/documents/`               | List documents                |
| `GET`    | `/documents/database`        | List from vector store        |
| `GET`    | `/documents/{id}/stats`     | Document statistics           |
| `DELETE` | `/documents/{id}`           | Delete document               |
| `POST`   | `/chat/`                    | Chat query                    |
| `POST`   | `/chat/stream`              | Streaming chat                |
| `GET`    | `/chat/history/{session_id}`| Chat history                  |
| `DELETE` | `/chat/history/{session_id}`| Clear history                |
| `POST`   | `/chat/ingest-text`         | Ingest raw text               |

---

### Health Check

#### `GET /health`

**Response:**

```json
{
  "status": "ok",
  "qdrant_connected": true,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "llm_provider": "deepseek"
}
```

---

### Upload Document

#### `POST /documents/upload`

**Request:** `multipart/form-data`

| Field     | Type   | Required | Description      |
| --------- | ------ | -------- | ---------------- |
| `file`    | file   | Yes      | Document file    |
| `title`   | string | No       | Document title   |

**Response:**

```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "chunks": 15,
  "status": "success"
}
```

---

### Chat with RAG

#### `POST /chat/`

**Request:**

```json
{
  "query": "What is the main topic?",
  "session_id": "optional-session-id",
  "doc_ids": ["doc-id-1"],
  "top_k": 5,
  "temperature": 0.7
}
```

**Response:**

```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "text": "Document excerpt...",
      "score": 0.95,
      "metadata": {"source": "pdf", "filename": "doc.pdf"}
    }
  ],
  "session_id": "session-uuid",
  "model": "deepseek-chat",
  "processing_time_ms": 1234.5
}
```

---

### Streaming Chat

#### `POST /chat/stream`

**Request:** Same as `/chat/`

**Response:** Server-Sent Events (SSE)

```
data: Based

data:  on

data:  the

data: [DONE]

event: meta
data: {"model": "deepseek-chat"}
```

---

## Media Generation Service (Port 8015)

Base URL: `http://localhost:8015`

Text-to-Image generation using Stable Diffusion.

### Endpoints Overview

| Method | Endpoint           | Description            |
| ------ | ------------------ | ---------------------- |
| `GET`  | `/health`          | Health check           |
| `POST` | `/image/generate`  | Generate image         |
| `POST` | `/cache/clear`     | Clear model cache      |

---

### Health Check

#### `GET /health`

**Response:**

```json
{
  "status": "ok",
  "model": "runwayml/stable-diffusion-v1-5",
  "device": "mps",
  "cuda_available": false,
  "mps_available": true,
  "cuda_device_count": 0,
  "pipeline_loaded": true
}
```

---

### Generate Image

#### `POST /image/generate`

**Request:**

```json
{
  "prompt": "A serene mountain landscape at sunset",
  "negative_prompt": "blurry, low quality, distorted",
  "width": 512,
  "height": 512,
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "seed": null
}
```

**Response:**

```json
{
  "images": ["data:image/png;base64,..."],
  "seed": 12345,
  "processing_time_ms": 5234.5
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {"loc": ["body", "field"], "msg": "Field required", "type": "missing"}
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Environment Variables

### Text Service

| Variable           | Default | Description          |
| ------------------ | ------- | -------------------- |
| `LLM_PROVIDER`     | openai  | Default LLM provider |
| `LLM_MODEL`        | gpt-4o-mini | Default model     |
| `OPENAI_API_KEY`   | -       | OpenAI API key       |
| `ANTHROPIC_API_KEY`| -       | Anthropic API key    |
| `OLLAMA_BASE_URL`  | localhost:11434 | Ollama URL    |

### TTS Service

| Variable        | Default | Description        |
| --------------- | ------- | ------------------ |
| `TTS_PROVIDER`  | edge    | Default TTS provider |

### RAG Service

| Variable          | Default          | Description           |
| ----------------- | ---------------- | --------------------- |
| `PORT`            | 8010             | Service port          |
| `QDRANT_HOST`     | localhost        | Qdrant server host    |
| `QDRANT_PORT`     | 6333            | Qdrant server port    |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embedding model      |
| `LLM_PROVIDER`    | deepseek        | RAG LLM provider      |

### Media Generation Service

| Variable    | Default                      | Description         |
| ----------- | ---------------------------- | ------------------- |
| `PORT`      | 8015                         | Service port        |
| `SD_MODEL`  | runwayml/stable-diffusion-v1-5 | Stable Diffusion model |
| `HF_TOKEN`  | -                            | HuggingFace token   |

---

## Client Examples

### Python with `requests`

```python
import requests

# Text Service
response = requests.post(
    "http://localhost:8006/api/text/chat",
    json={"messages": [{"role": "user", "content": "Hello"}]}
)
print(response.json())

# TTS Service
response = requests.post(
    "http://localhost:8005/tts/synthesize",
    json={"text": "Hello", "voice": "en-US-JennyNeural"}
)
with open("output.mp3", "wb") as f:
    f.write(response.content)

# RAG Service
response = requests.post(
    "http://localhost:8010/chat/",
    json={"query": "What is AI?"}
)
print(response.json())

# Media Generation
response = requests.post(
    "http://localhost:8015/image/generate",
    json={"prompt": "A cat"}
)
print(response.json())
```

### cURL

```bash
# Text Service
curl -X POST http://localhost:8006/api/text/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# TTS Service
curl -X POST http://localhost:8005/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "voice": "en-US-JennyNeural"}'

# RAG - Upload
curl -X POST http://localhost:8010/documents/upload \
  -F "file=@document.pdf"

# RAG - Chat
curl -X POST http://localhost:8010/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'

# Media Generation
curl -X POST http://localhost:8015/image/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset"}'
```
