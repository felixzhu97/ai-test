# AI-Test Platform

企业级 AI 基础设施管理平台，提供多智能体协作、RAG 文档问答、文本生成、语音合成、图像生成等能力。

## 服务概览

| 服务 | 端口 | 技术栈 | 功能 |
|------|------|--------|------|
| Text Service | 8006 | FastAPI | GPT/Claude/Ollama 文本生成 |
| TTS Service | 8005 | FastAPI | Azure/Google/ElevenLabs/Coqui 语音合成 |
| RAG Service | 8001 | FastAPI + Qdrant | 文档检索增强生成 |
| Media Gen | 3456 | FastAPI + Diffusers | Stable Diffusion 文生图 |
| Vision Service | 8000 | FastAPI + PyTorch | YOLO、BLIP、OCR 视觉分析 |
| AI Agents | 8003 | FastAPI + LangGraph | 多智能体编排 |

## 快速开始

### 前置要求

- Node.js >= 20
- pnpm >= 9
- Python >= 3.9
- (可选) NVIDIA GPU + CUDA

### 启动所有服务

```bash
# 安装依赖
pnpm install

# 启动服务
pnpm start
```

### 单独启动服务

```bash
# Text Service
cd services/text-service && uvicorn src.main:app --port 8006

# TTS Service
cd services/tts-service && uvicorn src.main:app --port 8005

# RAG Service
cd services/rag && uvicorn src.main:app --port 8001

# Media Gen
cd services/media-gen && uvicorn app:app --port 3456

# Vision Service
cd services/vision-service && uvicorn src.main:app --port 8000

# AI Agents
cd services/ai_agents && uvicorn main:app --port 8003
```

## 文档

| 文档 | 说明 |
|------|------|
| [快速开始](./QUICKSTART.md) | 5 分钟快速上手 |
| [架构设计](./ARCHITECTURE.md) | 系统设计与组件概览 |
| [API 参考](./API.md) | REST API 端点 |
| [开发指南](./DEVELOPMENT.md) | 本地开发环境配置 |
| [C4 模型](./c4/README.md) | 架构 C4 模型图 |
