# Architecture Overview

## System Architecture

The AI-Test Platform is a full-stack application with a microservices-inspired architecture:

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
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Agents Service Layer                       │
│               (Python + FastAPI + LangGraph)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Supervisor Agent                        │   │
│  │         (Central Coordinator - Task Routing)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│    ┌───────┬───────┬───────┬───────┬───────┬───────┬───────┐   │
│    ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼   │
│ ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐   │
│ │K8s  ││Vec  ││RAG  ││Pipe ││LLM  ││AIOps││Moni ││Model│   │
│ └─────┘└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                    Vision Service Layer                         │
│                 (FastAPI + Python + DDD)                        │
│         ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│         │     YOLO    │  │     BLIP    │  │    PaddleOCR    │  │
│         └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Service Layer                            │
│                 (FastAPI + Python)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Document   │  │   Embedding  │  │      LLM Gateway     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## AI Agents Multi-Agent System

### Architecture

The AI Agents service uses a **Supervisor-based routing pattern** where a central Supervisor Agent coordinates 12 specialized agents via keyword-based routing.

```
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                          │
│            (Central Coordinator & Router)                    │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Intent Detection → Agent Selection → Delegation     │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  K8s Agent    │   │  VectorDB     │   │  RAG Agent    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌───────────────┐
                    │   Tools       │
                    │ - HTTP Tools  │
                    │ - System Tools│
                    │ - 50+ Special │
                    └───────────────┘
```

### Core Agents


| Agent             | Responsibility                                      |
| ----------------- | --------------------------------------------------- |
| **Supervisor**    | Central coordinator, intent detection, task routing |
| **K8s**           | Kubernetes management (pods, services, scaling)     |
| **VectorDB**      | Vector embeddings and similarity search             |
| **RAG**           | Document retrieval and knowledge base               |
| **Pipeline**      | Workflow orchestration (DAG execution)              |
| **LLMOps**        | LLM training, fine-tuning, evaluation               |
| **AIOps**         | Anomaly detection, incident management              |
| **Feature Store** | Feature engineering and materialization             |
| **Monitoring**    | Metrics, logs, alerting                             |
| **Model**         | ML model lifecycle management                       |
| **TTS**           | Text-to-speech synthesis                            |
| **Video**         | Video generation                                    |


### Routing Configuration

```
用户输入 → Supervisor → 关键词匹配 → 专业智能体

├── "vector", "embedding"     → VectorDB Agent
├── "k8s", "pod", "cluster"   → K8s Agent
├── "monitor", "metric"       → Monitoring Agent
├── "model", "ml", "version"  → Model Agent
├── "rag", "document"        → RAG Agent
├── "pipeline", "dag"        → Pipeline Agent
├── "aiops", "anomaly"        → AIOps Agent
├── "tts", "speech"           → TTS Agent
├── "video", "generate"       → Video Agent
```

## Core Services

### 1. Web Frontend (`apps/web`)

React 18 SPA with Apple-style aesthetics. Provides user interface for agent interactions, real-time chat with streaming responses, and multi-language i18n support.

**Tech Stack:** React 18, Vite, TypeScript, Emotion CSS-in-JS

### 2. AI Agents Service (`services/ai_agents`)

The core multi-agent orchestration service. Coordinates 12 specialized agents via Supervisor-based routing, with 58+ specialized tools and LangGraph workflows for complex operations.

**Tech Stack:** FastAPI, Python 3.10+, LangChain/LangGraph, Ollama

### 3. Vision Service (`services/vision-service`)

Computer vision and image/video generation with **Domain-Driven Design (DDD)** architecture.

#### DDD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Presentation Layer (API)                      │
│         api/vision.py | api/image_gen.py | api/video.py          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                              │
│              use_cases/ | dtos/                                   │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                                │
│        entities/ | value_objects/ | services/ | events/         │
│              VideoTask (state machine), Image entities            │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                           │
│              providers/ | core/ (DI container)                   │
│       Kling, Pika, Runway, Sora, Replicate, Mock providers       │
└─────────────────────────────────────────────────────────────────┘
```

**Responsibilities:** Image processing (YOLO, BLIP, PaddleOCR), image generation (Stable Diffusion), video generation (Sora, Pika, Runway, Kling), multi-provider abstraction.

### 4. RAG Service (`services/rag`)

Retrieval-Augmented Generation with Qdrant vector store, LLM-powered Q&A, and multi-layer caching.

**Tech Stack:** FastAPI, Qdrant, LangChain, SQLite (sessions)

### 5. Text Service (`services/text-service`)

Text-to-Text LLM service supporting OpenAI GPT, Anthropic Claude, and Ollama with streaming responses.

### 6. TTS Service (`services/tts-service`)

Text-to-Speech with multi-provider support (Azure, Google, ElevenLabs, Coqui).

### 7. Media Gen Service (`services/media-gen`)

Local Text-to-Image generation using Stable Diffusion with Diffusers library.

## Data Flow

```
User Input → React App → HTTP POST → AI Agents Service (8003)
                                          │
                                          ▼
                                    Supervisor Agent
                                          │
                                          ▼
                              Intent Detection & Routing
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
              K8s Agent              VectorDB Agent        Monitoring Agent
                    │                     │                     │
                    ▼                     ▼                     ▼
              K8s Tools             Vector Tools          Monitoring Tools
                                          │
                                          ▼
                              Streaming Response (SSE)
```

## Directory Structure

```
ai-test/
├── apps/
│   ├── web/                    # React frontend
│   │   ├── src/components/     # UI components (panels, agents, AIHub)
│   │   ├── src/i18n/          # Internationalization
│   │   └── src/theme.ts        # Theme system
│   └── server/                 # Express.js server
├── packages/
│   ├── config/                 # Shared TypeScript config
│   └── utils/                  # Shared utilities
├── services/
│   ├── ai_agents/              # AI Agents (Supervisor + 12 agents)
│   │   ├── agents/             # Specialized agents
│   │   ├── tools/              # 58+ tools (http, system, k8s, etc.)
│   │   └── graphs/             # LangGraph workflows
│   ├── vision-service/         # Vision AI (DDD Architecture)
│   │   ├── src/api/            # Presentation Layer
│   │   ├── src/application/    # Application Layer (use_cases, dtos)
│   │   ├── src/domain/         # Domain Layer (entities, services)
│   │   └── src/providers/      # Infrastructure (AI providers)
│   ├── rag/                    # RAG service
│   │   └── src/persistence/    # Cache, sessions, metadata
│   ├── text-service/           # Text LLM service
│   ├── tts-service/             # Text-to-Speech
│   └── media-gen/               # Stable Diffusion
└── docs/
```

## API Reference

See [API.md](API.md) for detailed API documentation.

### Quick Overview


| Service   | Port | Key Endpoints                                              |
| --------- | ---- | ---------------------------------------------------------- |
| AI Agents | 8003 | `/api/agents/supervisor/invoke`                            |
| Vision    | 8000 | `/vision/detect`, `/image-gen/generate`, `/video/generate` |
| RAG       | 8001 | `/documents/ingest`, `/chat`                               |
| TTS       | 8005 | `/tts/synthesize`, `/tts/voices`                           |
| Text      | 8006 | `/api/text/complete`, `/api/text/chat`                     |


## Configuration

```env
# AI Agents
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# Vision Service
DEVICE=cuda                    # 'cuda' or 'cpu'
MAX_IMAGE_SIZE=10485760        # 10MB
```

## Deployment

- **Docker Compose** (Recommended): GPU variant for production, CPU variant for dev
- **Kubernetes**: GPU node pools for AI services
- **Cloud**: AWS ECS/EKS, GCP Cloud Run, Azure Container Instances

## C4 Model

Detailed C4 architecture diagrams are maintained separately. See:

- [C4 Model Documentation](path/to/c4-model)

