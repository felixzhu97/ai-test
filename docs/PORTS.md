# Service Ports Configuration

Standard port assignments for AI-Test platform services.

## Port Assignment Table

| Service              | Port | Protocol | Description                              |
| -------------------- | ---- | ------- | ---------------------------------------- |
| Text Service         | 8006 | HTTP    | Text generation with LLM providers       |
| TTS Service          | 8005 | HTTP    | Text-to-Speech synthesis                 |
| RAG Service          | 8010 | HTTP    | Retrieval-augmented generation           |
| Media Generation     | 8015 | HTTP    | Text-to-image (Stable Diffusion)         |

### Supporting Services

| Service      | Port      | Description              |
| ------------ | --------- | ----------------------- |
| Qdrant       | 6333/6334 | Vector database for RAG |
| Ollama       | 11434     | Local LLM inference     |
| Redis        | 6379      | Optional cache backend  |

---

## API Endpoints Summary

### Text Service (8006)

| Method   | Endpoint                    | Description              |
| -------- | --------------------------- | ---------------------- |
| `GET`    | `/api/text/health`          | Health check            |
| `GET`    | `/api/text/providers`       | List LLM providers      |
| `GET`    | `/api/text/models`         | List available models   |
| `POST`   | `/api/text/complete`       | Text completion         |
| `POST`   | `/api/text/complete/stream`| Stream completion       |
| `POST`   | `/api/text/chat`           | Chat completion         |
| `POST`   | `/api/text/chat/stream`    | Stream chat completion  |
| `GET`    | `/api/text/session/{id}`   | Session history         |
| `DELETE` | `/api/text/session/{id}`   | Clear session           |
| `POST`   | `/api/text/reset`          | Reset LLM cache         |

### TTS Service (8005)

| Method | Endpoint            | Description            |
| ------ | ------------------- | ---------------------- |
| `GET`  | `/tts/health`       | Health check           |
| `GET`  | `/tts/voices`       | List voices            |
| `GET`  | `/tts/providers`    | List TTS providers     |
| `GET`  | `/tts/provider`    | Get current provider    |
| `POST` | `/tts/synthesize`  | Synthesize speech      |
| `POST` | `/tts/stream`      | Stream speech          |

### RAG Service (8010)

| Method   | Endpoint                    | Description          |
| -------- | --------------------------- | ------------------- |
| `GET`    | `/health`                  | Health check        |
| `POST`   | `/documents/upload`        | Upload document     |
| `POST`   | `/documents/ingest-url`    | Ingest from URL     |
| `GET`    | `/documents/`             | List documents      |
| `GET`    | `/documents/database`     | List from vector DB |
| `GET`    | `/documents/{id}/stats`   | Document stats      |
| `DELETE` | `/documents/{id}`         | Delete document     |
| `POST`   | `/chat/`                  | Chat query          |
| `POST`   | `/chat/stream`            | Streaming chat      |
| `GET`    | `/chat/history/{session}`  | Chat history        |
| `DELETE` | `/chat/history/{session}` | Clear history       |
| `POST`   | `/chat/ingest-text`       | Ingest raw text     |

### Media Generation Service (8015)

| Method | Endpoint              | Description           |
| ------ | --------------------- | --------------------- |
| `GET`  | `/health`             | Health check          |
| `POST` | `/image/generate`     | Generate image        |
| `POST` | `/cache/clear`        | Clear model cache     |

---

## Domain Ports (Interfaces)

### Text Service Domain Ports

| Port                    | Location                                | Description                     |
| ----------------------- | --------------------------------------- | ------------------------------ |
| `ChatMessage`           | `src/domain/entities/message.py`        | Chat message value object      |
| `LLM Gateway Protocol`  | `src/infrastructure/gateways/llm_protocol.py` | LLM interface (Adapter pattern) |

### TTS Service Domain Ports

| Port                   | Location                              | Description                    |
| ---------------------- | ------------------------------------- | ----------------------------- |
| `TTSProviderPort`      | `src/domain/ports/tts_provider.py`    | TTS provider interface         |
| `Voice`                | `src/domain/entities/voice.py`         | Voice entity                  |
| `SynthesisRequest`     | `src/domain/entities/synthesis.py`    | Synthesis request entity      |
| `OutputFormat`         | `src/domain/entities/audio_config.py` | Audio output format enum      |

### RAG Service Domain Ports

| Port                    | Location                              | Description                     |
| ----------------------- | ------------------------------------- | ------------------------------ |
| `VectorStorePort`       | `src/domain/ports/vector_store.py`     | Vector storage interface        |
| `EmbeddingPort`         | `src/domain/ports/embedding.py`        | Embedding generation interface  |
| `LLMGatewayPort`        | `src/domain/ports/llm.py`             | LLM interface                  |
| `CachePort`             | `src/domain/ports/cache.py`            | Cache interface                |
| `DocumentRepositoryPort`| `src/domain/ports/document_repository.py`| Document persistence interface |

### Media Generation Domain Ports

| Port                  | Location                                   | Description                  |
| --------------------- | ------------------------------------------ | ---------------------------- |
| `ImageEncoderPort`    | `src/domain/ports/image_encoder_port.py`    | Image encoding interface     |
| `ModelCacheRepository`| `src/domain/repositories/model_cache_repository.py` | Model cache interface |

---

## Environment Variables

### Frontend (apps/web/.env)

```env
VITE_TEXT_SERVICE_URL=http://localhost:8006
VITE_SPEECH_SERVICE_URL=http://localhost:8005
VITE_RAG_SERVICE_URL=http://localhost:8010
```

### Backend Service Ports

| Service              | Config File                    | Default |
| -------------------- | ------------------------------ | ------- |
| Text Service         | `text-service/src/core/config.py` | 8006   |
| TTS Service          | `tts-service/src/config.py`      | 8005   |
| RAG Service          | `rag/src/config.py`              | 8010   |
| Media Generation     | `media-gen/src/core/settings.py` | 8015   |

---

## Common Issues

1. **Port Already in Use**
   ```bash
   lsof -i :8006
   kill -9 <PID>
   ```

2. **CORS Errors**
   All services have CORS configured. Verify services are running.

3. **Service-to-Service Communication**
   Services use localhost URLs. Ensure all required services are running.
