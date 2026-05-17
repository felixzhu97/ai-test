# Architecture Overview

## System Architecture

The AI-Test Platform is a microservices-based AI service platform with five core services, each following Clean Architecture and DDD principles.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│                    (React + Vite SPA)                           │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│                   (Express.js Server)                           │
└─────────────────────────────────────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Text Service   │  │   RAG Service   │  │   TTS Service   │
│   (Port 8006)   │  │   (Port 8001)   │  │   (Port 8005)   │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │   Lang    │  │  │  │ Sentence │  │  │  │   Edge    │  │
│  │   Chain   │  │  │  │Transformer│  │  │  │   TTS     │  │
│  │   LLM     │  │  │  └───────────┘  │  │  └───────────┘  │
│  └───────────┘  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  ┌───────────┐  │  │  │  Qdrant   │  │  │  │  Azure    │  │
│  │  Session  │  │  │  │  Vector   │  │  │  │  Google   │  │
│  │  Repo     │  │  │  └───────────┘  │  │  │ ElevenLabs│  │
│  └───────────┘  │  └─────────────────┘  │  └───────────┘  │
└─────────────────┘                       └─────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Media Gen Svc   │  │ Vision Service  │  │   Other AI     │
│   (Local SD)    │  │   (Port 8000)   │  │   Services     │
│  ┌───────────┐  │  │  ┌───────────┐  │  │                │
│  │ Stable    │  │  │  │  YOLO     │  │  │                │
│  │ Diffusion │  │  │  │  BLIP     │  │  │                │
│  │ Pipeline  │  │  │  │ PaddleOCR │  │  │                │
│  └───────────┘  │  │  └───────────┘  │  │                │
│  ┌───────────┐  │  │  ┌───────────┐  │  │                │
│  │ Hugging   │  │  │  │  Kling    │  │  │                │
│  │  Face     │  │  │  │  Runway   │  │  │                │
│  └───────────┘  │  │  │  Pika     │  │  │                │
└─────────────────┘  │  └───────────┘  │  └─────────────────┘
                     └─────────────────┘
```

## Core Services

### 1. Text Service (`services/text-service`)

Text-to-Text LLM service with session management and multi-provider support.

**Tech Stack:** FastAPI, LangChain, Python 3.10+

**Architecture (Clean Architecture + DDD):**

```
Presentation Layer (API)
├── routes.py          # FastAPI endpoints
├── schemas.py         # Pydantic request/response models
└── dependencies.py   # Dependency injection

Application Layer
├── use_cases/
│   ├── chat_use_case.py        # Chat completion with session
│   └── completion_use_case.py  # Simple text completion
└── dto/
    ├── chat_dto.py      # Chat DTOs
    └── completion_dto.py

Domain Layer (Pure Business Logic)
├── entities/
│   ├── message.py       # ChatMessage value object
│   └── session.py       # Session aggregate root
├── value_objects/
│   └── provider.py      # LLMProvider enum
└── repositories/
    └── session_repository.py  # Repository interface

Infrastructure Layer
├── gateways/
│   ├── langchain_llm_gateway.py  # LangChain implementation
│   ├── llm_protocol.py           # Port interface
│   └── config_adapter.py         # Configuration port
└── repositories/
    └── in_memory_session_repository.py

Ports:
├── LLMGatewayPort - LLM invocation interface
└── SessionRepository - Session persistence interface
```

**Key Entities:**
- `Session` - Aggregate root managing conversation history with max_history trimming
- `ChatMessage` - Immutable value object for messages
- `LLMProvider` - Enum (OPENAI, ANTHROPIC, OLLAMA)

**API Endpoints (Port 8006):**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/text/health` | GET | Health check |
| `/api/text/providers` | GET | List available LLM providers |
| `/api/text/models` | GET | List available models |
| `/api/text/complete` | POST | Generate text completion |
| `/api/text/complete/stream` | POST | Stream completion (SSE) |
| `/api/text/chat` | POST | Chat completion with session |
| `/api/text/chat/stream` | POST | Stream chat (SSE) |
| `/api/text/session/{id}` | GET/DELETE | Session management |

---

### 2. TTS Service (`services/tts-service`)

Text-to-Speech synthesis with multi-provider abstraction and DDD architecture.

**Tech Stack:** FastAPI, edge-tts, azure-cognitiveservices-speech, Python 3.10+

**Architecture:**

```
Domain Layer
├── entities/
│   ├── voice.py           # Voice value object (frozen dataclass)
│   ├── synthesis.py       # SynthesisRequest, SynthesisResult
│   └── audio_config.py    # AudioConfig value object
├── services/
│   └── synthesis_service.py  # Business logic (text normalization, SSML)
└── ports/
    └── tts_provider.py    # TTSProviderPort interface

Application Layer
├── services/
│   └── tts_application_service.py  # Facade orchestrating use cases
├── use_cases/
│   ├── synthesize_speech.py   # Batch synthesis
│   ├── stream_speech.py       # Streaming synthesis
│   ├── list_voices.py         # Voice listing
│   └── get_health.py         # Health check
└── dtos/
    └── synthesis_dto.py       # Request/Response DTOs

Infrastructure Layer
└── adapters/
    ├── edge_tts_adapter.py      # Microsoft Edge TTS (default)
    ├── azure_tts_adapter.py     # Azure Cognitive Services
    ├── google_tts_adapter.py    # Google Cloud TTS
    ├── elevenlabs_tts_adapter.py # ElevenLabs
    ├── coqui_tts_adapter.py     # Coqui TTS (local)
    └── base_adapter.py          # Base adapter with common logic

Presentation Layer
├── routers/
│   ├── tts.py              # API endpoints
│   └── dependencies.py     # DI setup
```

**Key Entities:**
- `Voice` - Immutable voice descriptor with language/gender filtering
- `SynthesisRequest` - Domain entity for synthesis parameters
- `SynthesisResult` - Immutable result with audio data
- `AudioConfig` - Immutable audio configuration (sample_rate, bit_rate, channels)

**Domain Service:**
- `SynthesisService` - Text normalization, SSML generation, speed/pitch transformation

**API Endpoints (Port 8005):**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tts/health` | GET | Health check |
| `/tts/synthesize` | POST | Synthesize speech (returns audio) |
| `/tts/stream` | POST | Stream speech |
| `/tts/voices` | GET | List available voices |
| `/tts/providers` | GET | List TTS providers |

---

### 3. RAG Service (`services/rag`)

Retrieval-Augmented Generation with Qdrant vector store and multi-layer caching.

**Tech Stack:** FastAPI, Qdrant, LangChain, Sentence Transformers, Python 3.10+

**Architecture:**

```
Application Layer
├── document_service.py      # Document upload, ingestion, retrieval
├── rag_chain_service.py     # RAG chain orchestration
└── dependencies.py          # Dependency injection

Domain Layer
└── ports/
    ├── document_repository.py  # Document persistence interface
    ├── vector_store.py         # Vector storage interface
    ├── embedding.py            # Embedding generation interface
    ├── llm.py                  # LLM interface
    └── cache.py                # Cache interface

Infrastructure Layer
└── adapters/
    ├── qdrant_vector_store.py       # Qdrant implementation
    ├── sentence_transformer_embedding.py  # Sentence-BERT embeddings
    ├── langchain_llm_gateway.py      # LLM with LangChain
    └── cache_adapter.py             # Redis/file cache

Presentation Layer
├── chat.py      # Chat endpoints
└── documents.py # Document management endpoints
```

**Domain Ports:**
- `VectorStorePort` - Search, upsert, delete operations
- `EmbeddingPort` - Query/document embedding generation
- `LLMGatewayPort` - LLM generation with streaming
- `CachePort` - Multi-layer caching (memory + disk)
- `DocumentRepositoryPort` - Document metadata storage

**Key Components:**
- `DocumentService` - Upload, ingest, chunk text, upsert vectors
- `RAGChainService` - Query embedding, similarity search, context building, LLM generation

**API Endpoints (Port 8001):**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents/ingest` | POST | Upload and ingest document |
| `/documents/list` | GET | List documents |
| `/documents/{id}` | GET/DELETE | Get/delete document |
| `/chat` | POST | RAG chat |
| `/chat/stream` | POST | Stream chat response |

---

### 4. Media Gen Service (`services/media-gen`)

Local text-to-image generation using Stable Diffusion.

**Tech Stack:** FastAPI, Diffusers, PyTorch, Python 3.10+

**Architecture:**

```
Domain Layer
├── entities/
│   └── generated_image.py    # GeneratedImage entity
├── value_objects/
│   └── generation_params.py  # GenerationParams (validated)
├── ports/
│   └── image_encoder_port.py # ImageEncoderPort interface
└── repositories/
    └── model_cache_repository.py  # ModelCacheRepository interface

Application Layer
└── use_cases/
    └── generate_image_use_case.py  # Image generation logic

Infrastructure Layer
├── adapters/
│   ├── stable_diffusion_adapter.py  # SD pipeline with caching
│   └── image_encoder_adapter.py    # Base64 encoding
└── config/
    ├── device_selector.py     # CUDA/CPU selection
    └── huggingface_config.py  # HuggingFace settings

Presentation Layer
└── routes/
    ├── image_routes.py   # API endpoints
    └── health_routes.py  # Health check
```

**Key Entities:**
- `GeneratedImage` - Immutable image result with metadata
- `GenerationParams` - Validated generation parameters (steps, guidance_scale, width, height, seed)

**Key Ports:**
- `ModelCacheRepository` - Pipeline caching with lazy loading
- `ImageEncoderPort` - Image encoding interface

**API Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/image/generate` | POST | Generate images |

---

### 5. Vision Service (`services/vision-service`)

Computer vision service with DDD architecture for image analysis and video generation.

**Tech Stack:** FastAPI, YOLO, BLIP, PaddleOCR, Kling, Runway, Pika, Python 3.10+

**Architecture:**

```
Domain Layer
├── entities/
│   ├── image.py            # ImageGeneration entity
│   └── video_task.py       # VideoTask state machine
├── services/
│   ├── video_generation_service.py
│   ├── image_generation_service.py
│   └── image_generation_rules.py  # Prompt validation
├── value_objects/
│   └── common.py           # Dimensions, etc.
└── ports/
    ├── image_analysis.py   # YOLO, OCR interfaces
    ├── image_providers.py  # Image gen providers
    └── video_providers.py # Video gen providers

Application Layer
└── use_cases/
    ├── generate_image.py    # Image generation
    ├── generate_video.py   # Video generation
    ├── analyze_image.py    # Image analysis
    └── check_video_status.py

Infrastructure Layer
├── providers/             # External AI providers
│   ├── kling.py, runway.py, pika.py, sora.py  # Video
│   ├── replicate.py       # Image
│   └── mock.py            # Testing
└── models/               # Local ML models
    ├── yolo_detector.py
    ├── blip_captioner.py
    ├── paddle_ocr.py
    └── easy_ocr.py

Presentation Layer
└── api/
    ├── vision.py      # Detection, OCR endpoints
    ├── image_gen.py   # Image generation
    └── video.py       # Video generation
```

**Key Entities:**
- `ImageGeneration` - Image generation with validation
- `VideoTask` - Video generation state machine (PENDING, PROCESSING, COMPLETED, FAILED)

**API Endpoints (Port 8000):**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/vision/detect` | POST | Object detection (YOLO) |
| `/vision/ocr` | POST | Text recognition |
| `/vision/caption` | POST | Image captioning |
| `/image-gen/generate` | POST | Generate image |
| `/video/generate` | POST | Generate video |
| `/video/status/{id}` | GET | Check video status |

---

## Directory Structure

```
ai-test/
├── apps/
│   ├── web/                    # React frontend
│   │   ├── src/components/     # UI components
│   │   ├── src/i18n/          # Internationalization
│   │   └── src/theme.ts        # Theme system
│   └── server/                 # Express.js server
├── packages/
│   ├── config/                 # Shared TypeScript config
│   └── utils/                  # Shared utilities
├── services/
│   ├── text-service/           # Text LLM Service
│   │   ├── src/
│   │   │   ├── application/use_cases/
│   │   │   ├── domain/{entities,value_objects,repositories}/
│   │   │   ├── infrastructure/{gateways,repositories}/
│   │   │   └── presentation/api/
│   │   └── tests/
│   ├── tts-service/             # Text-to-Speech
│   │   ├── src/
│   │   │   ├── domain/{entities,services,ports}/
│   │   │   ├── application/{services,use_cases,dtos}/
│   │   │   ├── infrastructure/adapters/
│   │   │   └── presentation/routers/
│   │   └── tests/
│   ├── rag/                    # RAG Service
│   │   ├── src/
│   │   │   ├── application/
│   │   │   ├── domain/ports/
│   │   │   └── infrastructure/adapters/
│   │   └── tests/
│   ├── media-gen/               # Media Generation
│   │   ├── src/
│   │   │   ├── domain/{entities,value_objects,ports,repositories}/
│   │   │   ├── application/use_cases/
│   │   │   ├── infrastructure/{adapters,config}/
│   │   │   └── presentation/routes/
│   │   └── tests/
│   └── vision-service/         # Vision AI
│       ├── src/
│       │   ├── domain/{entities,services,ports}/
│       │   ├── application/use_cases/
│       │   ├── infrastructure/{providers,models}/
│       │   └── api/
│       └── tests/
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── c4/
```

---

## Data Flow

### Text Service Flow

```
Client Request
      │
      ▼
API Route (routes.py)
      │
      ▼
Use Case (ChatUseCase)
      │
      ├──► SessionRepository ──► InMemorySessionRepository
      │
      ▼
LLMGatewayPort ──► LangChainLLMGateway ──► OpenAI/Anthropic/Ollama
      │
      ▼
Session Update (add_assistant_message)
      │
      ▼
Response DTO ──► API Response
```

### RAG Service Flow

```
User Query
      │
      ▼
EmbeddingPort ──► SentenceTransformerEmbedding ──► Vector Store
      │                                              │
      ▼                                              ▼
VectorStorePort ──► QdrantVectorStore ──► Similarity Search
      │
      ▼
Context Building (search results → context string)
      │
      ▼
LLMGatewayPort ──► LangChainLLM ──► LLM Generation
      │
      ▼
CachePort ──► Response Caching
      │
      ▼
Chat Response + Source Documents
```

---

## API Reference Summary

| Service | Port | Key Endpoints |
|---------|------|----------------|
| Text | 8006 | `/api/text/chat`, `/api/text/complete`, `/api/text/chat/stream` |
| TTS | 8005 | `/tts/synthesize`, `/tts/stream`, `/tts/voices` |
| RAG | 8001 | `/chat`, `/documents/ingest` |
| Media Gen | 8002 | `/image/generate` |
| Vision | 8000 | `/vision/detect`, `/image-gen/generate`, `/video/generate` |

---

## Configuration

```env
# Text Service
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# TTS Service
TTS_PROVIDER=edge

# RAG Service
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Media Gen Service
DEVICE=cuda                    # 'cuda' or 'cpu'
SD_MODEL=runwayml/stable-diffusion-v1-5
HF_TOKEN=hf_...

# Vision Service
VISION_DEVICE=cuda
```

---

## C4 Model

Detailed C4 architecture diagrams are maintained in `docs/c4/`:

- `c4-context.puml` - System context
- `c4-container.puml` - Container-level architecture
- `c4-component-media-services.puml` - Media services component detail
