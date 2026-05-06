# Architecture Overview

## System Architecture

The AI Vision Service is a full-stack application with a microservices-inspired architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│                    (React + Vite SPA)                           │
│                       Port: 5173                                │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│                   (Express.js Server)                           │
│                     Ports: 3000-3001                            │
│               (Optional - Utility Endpoints)                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Service Layer                              │
│                 (FastAPI + Python)                              │
│                      Port: 8000                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │     YOLO     │  │     BLIP     │  │      PaddleOCR       │ │
│  │   Detector   │  │  Captioner   │  │      Processor       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Service Layer                             │
│                 (FastAPI + Python)                              │
│                      Port: 8001                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Document   │  │   Embedding  │  │      LLM Gateway     │ │
│  │    Loader    │  │    Model     │  │ (OpenAI/Claude/Ollama)│ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Qdrant Vector Store                             │
│                      Port: 6333                                   │
│         (Semantic Search & Document Storage)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Web Frontend (`apps/web`)

A single-page application built with React 18 and Vite.

**Responsibilities:**
- User interface for image upload
- Task selection (caption, detect, OCR, analyze)
- Display AI results with processing time
- Handle file drag-and-drop

**Tech Stack:**
- React 18
- Vite (bundler)
- TypeScript
- Native Fetch API

### 2. Backend Server (`apps/server`)

An Express.js server providing utility endpoints.

**Responsibilities:**
- Health check endpoint
- Random ID generation
- Utility functions (clamp, delay)

**Note:** This is currently optional and primarily serves as a reference implementation.

### 3. AI Service (`services/vision-service`)

The core FastAPI application providing vision AI capabilities.

**Responsibilities:**
- Image processing and validation
- Model inference (YOLO, BLIP, PaddleOCR)
- REST API endpoints
- Response serialization

### 4. RAG Service (`services/rag`)

A production-grade RAG (Retrieval-Augmented Generation) service.

**Responsibilities:**
- Document ingestion and processing
- Semantic vector search with Qdrant
- LLM-powered question answering
- Conversation history management

**Tech Stack:**
- FastAPI + Python 3.10+
- Qdrant vector database
- LangChain for RAG orchestration
- Sentence Transformers for embeddings
- Support for OpenAI, Anthropic Claude, Ollama

**Features:**
- Multi-format document support (PDF, Markdown, Web, Text)
- Streaming responses
- Session-based chat history
- Docker-ready deployment

## Data Flow

```
User Upload → React App → HTTP Request → FastAPI
                                              │
                                    ┌─────────┴─────────┐
                                    ▼                   ▼
                              load_image()         load_image()
                                    │                   │
                          ┌─────────┼─────────┐         │
                          ▼         ▼         ▼         │
                      YOLO       BLIP      PaddleOCR     │
                          │         │         │          │
                          └─────────┼─────────┘         │
                                    ▼                   │
                              Response ←── JSON ←───────┘
                                    │
                                    ▼
                              React App Display
```

## AI Models

### YOLO (Object Detection)

- **Purpose:** Identify and locate objects in images
- **Model:** YOLO11n (default) or custom YOLO models
- **Output:** Bounding boxes, class names, confidence scores
- **Device:** CUDA (GPU) or CPU

```python
# Usage in code
detector = YOLODetector()
result = await detector.detect(image, conf_threshold=0.25)
```

### BLIP (Image Captioning)

- **Purpose:** Generate natural language descriptions of images
- **Model:** Salesforce/blip-image-captioning-large (default)
- **Output:** Caption text with processing time
- **Device:** CUDA (GPU) or CPU

```python
# Usage in code
captioner = BLIPCaptioner()
result = await captioner.caption(image)
```

### PaddleOCR (Text Recognition)

- **Purpose:** Extract text from images
- **Languages:** Chinese, English (configurable)
- **Output:** Text blocks with bounding boxes and confidence
- **Device:** CUDA (GPU) or CPU

```python
# Usage in code
ocr = PaddleOCRProcessor()
result = await ocr.extract_text(image)
```

## Configuration

Configuration is managed through environment variables and the `.env` file:

```env
# AI Service Configuration
DEVICE=cuda                    # 'cuda' or 'cpu'
YOLO_MODEL=yolo11n.pt          # YOLO model path
BLIP_MODEL=Salesforce/blip-image-captioning-large
OCR_LANG=ch                 # OCR languages
MAX_IMAGE_SIZE=10485760        # 10MB max file size
MODEL_CACHE_DIR=./models       # Model cache location
MAX_CONCURRENT_REQUESTS=4      # Request queue limit
```

## Directory Structure

```
ai-test/
├── apps/
│   ├── web/                    # React frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   └── App.tsx
│   │   └── package.json
│   └── server/                 # Express.js server
│       ├── src/
│       │   └── index.ts
│       └── package.json
├── packages/
│   ├── config/                 # Shared TypeScript config
│   └── utils/                 # Shared utilities
├── services/
│   ├── vision-service/         # Python AI vision service
│   │   ├── src/
│   │   │   ├── main.py        # FastAPI app entry
│   │   │   ├── api/
│   │   │   │   └── vision.py  # Vision API routes
│   │   │   ├── models/
│   │   │   │   ├── yolo_detector.py
│   │   │   │   ├── blip_captioner.py
│   │   │   │   └── paddle_ocr.py
│   │   │   ├── schemas/
│   │   │   │   └── vision.py  # Pydantic models
│   │   │   └── core/
│   │   │       └── config.py # Settings
│   │   ├── tests/
│   │   │   ├── test_api.py
│   │   │   ├── test_config.py
│   │   │   └── test_schemas.py
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── pyproject.toml
│   └── rag/                    # RAG service (new)
│       ├── src/
│       │   ├── main.py        # FastAPI app entry
│       │   ├── config.py      # Settings
│       │   ├── schemas.py     # Pydantic models
│       │   ├── api/
│       │   │   ├── documents.py  # Document API
│       │   │   └── chat.py       # Chat API
│       │   ├── core/
│       │   │   ├── llm_gateway.py   # LLM abstraction
│       │   │   ├── embedding.py    # Embedding model
│       │   │   └── vector_store.py  # Qdrant integration
│       │   ├── document_loader/
│       │   │   └── loader.py       # Document loaders
│       │   └── services/
│       │       ├── ingestion.py     # Document ingestion
│       │       └── rag_chain.py    # RAG chain
│       ├── tests/
│       │   ├── conftest.py
│       │   └── test_rag_api.py
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── pyproject.toml
└── docs/                      # Documentation
```

## Request/Response Examples

### Object Detection Request

```bash
curl -X POST http://localhost:8000/vision/detect \
  -F "file=@image.jpg" \
  -F "conf=0.25"
```

### Object Detection Response

```json
{
  "task": "detect_objects",
  "model": "yolo11n.pt",
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.92,
      "bbox": [120, 50, 400, 600]
    }
  ],
  "image_width": 800,
  "image_height": 600,
  "processing_time_ms": 45.2
}
```

### Image Captioning Response

```json
{
  "task": "caption_image",
  "model": "Salesforce/blip-image-captioning-large",
  "caption": "A group of people hiking in the mountains",
  "processing_time_ms": 230.5
}
```

## Performance Considerations

### GPU Acceleration

The AI service uses CUDA by default for faster inference:

- **YOLO:** ~30-60 FPS on GPU, ~5-10 FPS on CPU
- **BLIP:** ~5-10 images/sec on GPU, ~0.5-1 images/sec on CPU
- **PaddleOCR:** ~10-20 images/sec on GPU, ~2-5 images/sec on CPU

### Concurrent Requests

The service limits concurrent requests to prevent memory issues:

```env
MAX_CONCURRENT_REQUESTS=4
```

### Image Size Limits

Maximum upload size is 10MB by default to prevent memory exhaustion.

## Security

- CORS is enabled for all origins (configure for production)
- File type validation (only images accepted)
- File size limits enforced
- No persistent storage of uploaded images

## Deployment Options

1. **Docker Compose (Recommended)**
   - GPU variant for production
   - CPU variant for development/low-resource environments

2. **Kubernetes**
   - Use GPU node pools for AI service
   - Scale horizontally with load balancer

3. **Cloud Services**
   - AWS: ECS + EKS with GPU instances
   - GCP: Cloud Run with GPU
   - Azure: Container Instances with GPU
