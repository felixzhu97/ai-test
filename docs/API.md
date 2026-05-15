# API Reference

REST API documentation for the AI-Test Platform services.

---

## Table of Contents

- [AI Agents Service (Port 8003)](#ai-agents-service-port-8003)
- [Vision Service (Port 8002)](#vision-service-port-8002)
- [RAG Service (Port 8001)](#rag-service-port-8001)

---

## AI Agents Service (Port 8003)

Base URL: `http://localhost:8003`

### Endpoints Overview


| Method | Endpoint                          | Description                                  |
| ------ | --------------------------------- | -------------------------------------------- |
| `GET`  | `/health`                         | Health check                                 |
| `GET`  | `/agents`                         | List all available agents                    |
| `POST` | `/api/agents/supervisor/invoke`   | Invoke supervisor agent (main chat endpoint) |
| `POST` | `/api/agents/{agent_name}/invoke` | Invoke a specific agent directly             |


---

### Health Check

#### `GET /health`

Check if the AI Agents service is running.

**Response:**

```json
{
  "status": "ok",
  "service": "ai_agents",
  "agents_initialized": true,
  "available_agents": ["vector", "kubernetes", "monitoring", "model", "rag", "llmops", "feature_store", "pipeline", "aiops"]
}
```

**Response Fields:**


| Field                | Type    | Description                     |
| -------------------- | ------- | ------------------------------- |
| `status`             | string  | Always `"ok"` if healthy        |
| `service`            | string  | Service identifier              |
| `agents_initialized` | boolean | Whether agents are loaded       |
| `available_agents`   | array   | List of initialized agent names |


---

### List Agents

#### `GET /agents`

Get information about all available agents.

**Response:**

```json
{
  "agents": [
    {
      "name": "vector",
      "description": "Handles vector database operations",
      "status": "online"
    },
    {
      "name": "kubernetes",
      "description": "Kubernetes cluster management",
      "status": "online"
    },
    {
      "name": "monitoring",
      "description": "Handles observability, metrics, logs, and alerting",
      "status": "online"
    },
    {
      "name": "model",
      "description": "Manages ML model lifecycle, deployment, and versioning",
      "status": "online"
    },
    {
      "name": "rag",
      "description": "Document retrieval and knowledge base management",
      "status": "online"
    },
    {
      "name": "llmops",
      "description": "ML model lifecycle management",
      "status": "online"
    },
    {
      "name": "feature_store",
      "description": "Feature engineering and management",
      "status": "online"
    },
    {
      "name": "pipeline",
      "description": "ML/DevOps workflow orchestration",
      "status": "online"
    },
    {
      "name": "aiops",
      "description": "Intelligent operations and anomaly detection",
      "status": "online"
    }
  ]
}
```

---

### Chat with Supervisor (Main Endpoint)

#### `POST /api/agents/supervisor/invoke`

Invoke the Supervisor agent to handle user queries. This is the main chat endpoint that routes to appropriate specialized agents.

**Request:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Show me the status of my kubernetes pods"
    }
  ]
}
```

**Request Fields:**


| Field                | Type   | Required | Description                           |
| -------------------- | ------ | -------- | ------------------------------------- |
| `messages`           | array  | Yes      | List of conversation messages         |
| `messages[].role`    | string | Yes      | Message role (`user`, `assistant`)    |
| `messages[].content` | string | Yes      | Message content                       |
| `agent_name`         | string | No       | Specific agent to route to (optional) |


**Response:**

Server-Sent Events (SSE) streaming response:

```
event: message
data: Starting analysis...

event: message
data: Routing to: kubernetes
...

event: message
data: Your kubernetes cluster has 3 pods running:
- nginx-deployment-abc123 (Running)
- redis-xyz789 (Running)
- api-gateway-def456 (Running)

event: tool_output
data: Agent 'kubernetes' completed

data: [DONE]
```

**Event Types:**


| Event         | Description                  |
| ------------- | ---------------------------- |
| `message`     | Text response from the agent |
| `tool_call`   | Tool invocation details      |
| `tool_output` | Result from tool execution   |
| `error`       | Error message                |
| `[DONE]`      | End of stream marker         |


---

### Invoke Specific Agent

#### `POST /api/agents/{agent_name}/invoke`

Invoke a specific agent directly without going through the Supervisor.

**Path Parameters:**


| Parameter    | Type   | Description                                             |
| ------------ | ------ | ------------------------------------------------------- |
| `agent_name` | string | Agent name (e.g., `vector`, `kubernetes`, `monitoring`) |


**Request:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Search for similar documents about machine learning"
    }
  ]
}
```

**Response:**

Server-Sent Events (SSE) streaming response (same format as supervisor endpoint).

**Available Agents:**


| Agent Name      | Description                             |
| --------------- | --------------------------------------- |
| `vector`        | Vector database operations              |
| `kubernetes`    | Kubernetes cluster management           |
| `monitoring`    | Metrics, logs, and alerting             |
| `model`         | ML model lifecycle management           |
| `rag`           | Document retrieval and knowledge base   |
| `llmops`        | LLM operations and experiments          |
| `feature_store` | Feature engineering                     |
| `pipeline`      | Workflow orchestration                  |
| `aiops`         | Anomaly detection and incident response |


---

### Example: Using cURL

```bash
# Health check
curl http://localhost:8003/health

# List agents
curl http://localhost:8003/agents

# Chat with Supervisor
curl -X POST http://localhost:8003/api/agents/supervisor/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What pods are running in my cluster?"}
    ]
  }'

# Query specific agent
curl -X POST http://localhost:8003/api/agents/vector/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Show me recent embeddings"}
    ]
  }'
```

---

## Vision Service (Port 8002)

Base URL: `http://localhost:8002`

### Endpoints Overview


| Method | Endpoint          | Description           |
| ------ | ----------------- | --------------------- |
| `GET`  | `/health`         | Health check          |
| `GET`  | `/`               | Service info          |
| `POST` | `/vision/detect`  | Object detection      |
| `POST` | `/vision/caption` | Image captioning      |
| `POST` | `/vision/ocr`     | Text extraction (OCR) |
| `POST` | `/vision/analyze` | Combined analysis     |


---

### Health Check

#### `GET /health`

Check if the service is running.

**Response:**

```json
{
  "status": "ok"
}
```

---

### Service Info

#### `GET /`

Get service information and available endpoints.

**Response:**

```json
{
  "name": "AI Vision Service",
  "version": "0.1.0",
  "endpoints": {
    "health": "/health",
    "detect": "/vision/detect",
    "caption": "/vision/caption",
    "ocr": "/vision/ocr",
    "analyze": "/vision/analyze"
  }
}
```

---

### Object Detection

#### `POST /vision/detect`

Detect objects in an image using YOLO.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file` (required): Image file (JPEG, PNG, etc.)
  - `conf` (optional): Confidence threshold (default: 0.25)

**Response:**

```json
{
  "task": "detect_objects",
  "model": "yolo11n.pt",
  "detections": [
    {
      "class_name": "person",
      "confidence": 0.92,
      "bbox": [120, 50, 400, 600]
    },
    {
      "class_name": "car",
      "confidence": 0.85,
      "bbox": [500, 300, 700, 500]
    }
  ],
  "image_width": 800,
  "image_height": 600,
  "processing_time_ms": 45.2
}
```

**Response Fields:**


| Field                     | Type   | Description                     |
| ------------------------- | ------ | ------------------------------- |
| `task`                    | string | Always `"detect_objects"`       |
| `model`                   | string | YOLO model name                 |
| `detections`              | array  | List of detected objects        |
| `detections[].class_name` | string | Object class label              |
| `detections[].confidence` | float  | Confidence score (0-1)          |
| `detections[].bbox`       | array  | Bounding box [x1, y1, x2, y2]   |
| `image_width`             | int    | Image width in pixels           |
| `image_height`            | int    | Image height in pixels          |
| `processing_time_ms`      | float  | Processing time in milliseconds |


**Example:**

```bash
curl -X POST http://localhost:8002/vision/detect \
  -F "file=@image.jpg" \
  -F "conf=0.5"
```

---

### Image Captioning

#### `POST /vision/caption`

Generate a natural language description of an image using BLIP.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file` (required): Image file (JPEG, PNG, etc.)

**Response:**

```json
{
  "task": "caption_image",
  "model": "Salesforce/blip-image-captioning-large",
  "caption": "A person hiking in the mountains during sunset",
  "processing_time_ms": 230.5
}
```

**Response Fields:**


| Field                | Type   | Description                     |
| -------------------- | ------ | ------------------------------- |
| `task`               | string | Always `"caption_image"`        |
| `model`              | string | BLIP model name                 |
| `caption`            | string | Generated caption               |
| `processing_time_ms` | float  | Processing time in milliseconds |


**Example:**

```bash
curl -X POST http://localhost:8002/vision/caption \
  -F "file=@image.jpg"
```

---

### OCR (Text Extraction)

#### `POST /vision/ocr`

Extract text from an image using PaddleOCR.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file` (required): Image file (JPEG, PNG, etc.)

**Response:**

```json
{
  "task": "extract_text",
  "model": "PaddleOCR",
  "results": [
    {
      "text": "Hello World",
      "confidence": 0.95,
      "bbox": [[10, 10], [100, 10], [100, 30], [10, 30]]
    },
    {
      "text": "Document Text",
      "confidence": 0.92,
      "bbox": [[10, 50], [200, 50], [200, 70], [10, 70]]
    }
  ],
  "full_text": "Hello World\nDocument Text",
  "processing_time_ms": 85.3
}
```

**Response Fields:**


| Field                  | Type   | Description                                       |
| ---------------------- | ------ | ------------------------------------------------- |
| `task`                 | string | Always `"extract_text"`                           |
| `model`                | string | Always `"PaddleOCR"`                              |
| `results`              | array  | List of detected text blocks                      |
| `results[].text`       | string | Extracted text                                    |
| `results[].confidence` | float  | Confidence score (0-1)                            |
| `results[].bbox`       | array  | Bounding box [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] |
| `full_text`            | string | All extracted text joined with newlines           |
| `processing_time_ms`   | float  | Processing time in milliseconds                   |


**Example:**

```bash
curl -X POST http://localhost:8002/vision/ocr \
  -F "file=@document.jpg"
```

---

### Combined Analysis

#### `POST /vision/analyze`

Run multiple AI tasks on a single image.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file` (required): Image file (JPEG, PNG, etc.)
  - `task` (required): Task type (query parameter)

**Task Types:**


| Task             | Description      | Response Keys                  |
| ---------------- | ---------------- | ------------------------------ |
| `caption_image`  | Generate caption | `caption`                      |
| `detect_objects` | Detect objects   | `detections`                   |
| `extract_text`   | Extract text     | `results`                      |
| `analyze_image`  | Run all tasks    | `caption`, `detections`, `ocr` |


**Example - Full Analysis:**

```bash
curl -X POST "http://localhost:8002/vision/analyze?task=analyze_image" \
  -F "file=@photo.jpg"
```

**Response:**

```json
{
  "caption": {
    "model": "Salesforce/blip-image-captioning-large",
    "caption": "A person reading a book",
    "processing_time_ms": 245.3
  },
  "detections": {
    "model": "yolo11n.pt",
    "detections": [...],
    "processing_time_ms": 48.1
  },
  "ocr": {
    "model": "PaddleOCR",
    "results": [...],
    "full_text": "Book title here",
    "processing_time_ms": 85.3
  }
}
```

---

## RAG Service (Port 8001)

Base URL: `http://localhost:8001`

### Endpoints Overview


| Method | Endpoint            | Description      |
| ------ | ------------------- | ---------------- |
| `GET`  | `/health`           | Health check     |
| `POST` | `/documents/ingest` | Ingest documents |
| `POST` | `/chat`             | Chat with RAG    |


---

### Health Check

#### `GET /health`

**Response:**

```json
{
  "status": "ok"
}
```

---

### Document Ingestion

#### `POST /documents/ingest`

Ingest documents into the knowledge base.

**Request:**

```json
{
  "text": "Your document content here...",
  "metadata": {
    "source": "manual",
    "category": "technical"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Document ingested successfully",
  "doc_id": "doc_abc123"
}
```

---

### Chat with RAG

#### `POST /chat`

Ask questions about the knowledge base.

**Request:**

```json
{
  "query": "What is the main topic of the documents?",
  "top_k": 5
}
```

**Response:**

```json
{
  "answer": "Based on the documents, the main topic appears to be...",
  "sources": [
    {
      "content": "Document excerpt...",
      "score": 0.95,
      "metadata": {"source": "manual"}
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request

Invalid image or file too large.

```json
{
  "detail": "Image too large (max 10MB)"
}
```

```json
{
  "detail": "Invalid image file"
}
```

### 422 Unprocessable Entity

Missing required fields.

```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### 500 Internal Server Error

Model or processing error.

```json
{
  "detail": "Model loading failed"
}
```

### 503 Service Unavailable

AI Agents service not initialized.

```json
{
  "detail": "Agents not initialized"
}
```

---

## Rate Limits

### Vision Service

- **Concurrent Requests:** 4 (configurable via `MAX_CONCURRENT_REQUESTS`)
- **Max File Size:** 10MB (configurable via `MAX_IMAGE_SIZE`)

---

## Environment Variables

### AI Agents Service


| Variable          | Default                  | Description       |
| ----------------- | ------------------------ | ----------------- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL`    | `qwen2.5:7b`             | Ollama model name |


### Vision Service


| Variable                  | Default                                  | Description                          |
| ------------------------- | ---------------------------------------- | ------------------------------------ |
| `DEVICE`                  | `cuda`                                   | Computation device (`cuda` or `cpu`) |
| `YOLO_MODEL`              | `yolo11n.pt`                             | YOLO model path                      |
| `BLIP_MODEL`              | `Salesforce/blip-image-captioning-large` | BLIP model name                      |
| `OCR_LANG`                | `ch`                                     | PaddleOCR language                   |
| `MAX_IMAGE_SIZE`          | `10485760`                               | Max file size in bytes (10MB)        |
| `MODEL_CACHE_DIR`         | `./models`                               | Model cache directory                |
| `MAX_CONCURRENT_REQUESTS` | `4`                                      | Max concurrent requests              |


---

## Client Examples

### Python with `requests`

```python
import requests

# AI Agents - Chat with Supervisor
response = requests.post(
    "http://localhost:8003/api/agents/supervisor/invoke",
    json={"messages": [{"role": "user", "content": "Hello"}]}
)
print(response.text)

# Vision - Object Detection
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8002/vision/detect",
        files={"file": f}
    )
print(response.json())
```

### JavaScript with `fetch`

```javascript
// AI Agents - Chat
const response = await fetch("http://localhost:8003/api/agents/supervisor/invoke", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    messages: [{role: "user", content: "Show me kubernetes pods"}]
  })
});

// Vision - Caption
const formData = new FormData();
formData.append("file", imageFile);

const visionResponse = await fetch("http://localhost:8002/vision/caption", {
  method: "POST",
  body: formData,
});

const data = await visionResponse.json();
console.log(data.caption);
```

### cURL

```bash
# AI Agents
curl http://localhost:8003/health
curl http://localhost:8003/agents

# Vision
curl -X POST http://localhost:8002/vision/caption \
  -F "file=@photo.jpg"

curl -X POST http://localhost:8002/vision/detect \
  -F "file=@photo.jpg" \
  -F "conf=0.5"

# RAG
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

