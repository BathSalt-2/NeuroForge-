# 🧠 NeuroForge

**AI-Powered Adaptive Learning Platform**

NeuroForge is an intelligent learning platform that combines an AI Mentor powered by **Gemma 4 E4B** (running locally via Ollama — no cloud API keys needed), a Knowledge Graph (Neo4j), cognitive profiling, and structured learning pathways to deliver personalized education experiences.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blueviolet) ![Python](https://img.shields.io/badge/Backend-Python%20%7C%20FastAPI-green) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![Gemma](https://img.shields.io/badge/LLM-Gemma%204%20E4B-4285F4) ![Neo4j](https://img.shields.io/badge/Graph%20DB-Neo4j-008CC1) ![Docker](https://img.shields.io/badge/Deploy-Docker%20Compose-2496ED)

---

## 🏗️ Architecture

NeuroForge is built as a **microservices architecture** with 7 backend services, an API gateway, a local LLM server (Ollama), and a React frontend — all orchestrated via Docker Compose.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│         Dashboard │ AI Mentor Chat │ Concepts │ Paths       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    API Gateway (:8000)                       │
│              Unified /api/v1/* routing + CORS                │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────┘
   │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│User  ││Know- ││AI    ││Cogni-││Cont- ││Learn-││ Neo4j│
│Svc   ││ledge ││Mentor││tive  ││ent   ││ing   ││ Seed │
│:8001 ││Graph ││Svc   ││Prof. ││Deliv.││Path  ││Runner│
│      ││:8002 ││:8003 ││:8004 ││:8005 ││:8006 ││      │
└──┬───┘└──┬───┘└──┬───┘└──────┘└──────┘└──┬───┘└──┬───┘
   │       │       │                        │       │
   ▼       ▼       ▼                        ▼       ▼
┌──────┐┌──────┐┌────────────┐        ┌──────┐┌──────┐
│Postgr││Neo4j ││   Ollama   │        │Postgr││Neo4j │
│  SQL ││      ││ Gemma 4 E4B│        │  SQL ││      │
└──────┘└──────┘└────────────┘        └──────┘└──────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **API Gateway** | 8000 | Unified entry point, routes to all services |
| **User Service** | 8001 | Registration, JWT auth, profile management |
| **Knowledge Graph Service** | 8002 | Concepts, skills, modules via Neo4j |
| **AI Mentor Service** | 8003 | LLM-powered tutoring (Gemma 4 E4B + KG context) |
| **Cognitive Profiling Service** | 8004 | Interaction logging, mock heatmaps |
| **Content Delivery Service** | 8005 | Learning module content (mock CDN) |
| **Learning Pathway Service** | 8006 | Path management, enrollment, progress |
| **Ollama** | 11434 | Local LLM server running Gemma 4 E4B |
| **Frontend** | 3000 | React SPA with dashboard, chat, browser |

---

## 🤖 LLM: Gemma 4 E4B (Local)

The AI Mentor runs entirely locally using Google's **Gemma 4 E4B** model served by **Ollama**. No cloud API keys or external services required.

| Property | Value |
|----------|-------|
| Model | Gemma 4 E4B (`gemma4:e4b`) |
| Parameters | 4.5B effective (8B with embeddings) |
| Context Window | 128K tokens |
| Download Size | ~9 GB |
| Runtime | Ollama (CPU or GPU) |

> **GPU acceleration:** Uncomment the `deploy.resources` block under the `ollama` service in `docker-compose.yml` if you have an NVIDIA GPU with `nvidia-container-toolkit` installed. The model runs on CPU by default — just slower.

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- ~12 GB free disk space (for model download + containers)
- 16 GB+ RAM recommended

### 1. Clone & configure

```bash
git clone https://github.com/BathSalt-2/NeuroForge-.git
cd NeuroForge-
cp .env.example .env
```

No API keys to configure — everything runs locally!

### 2. Start everything

```bash
docker compose up --build
```

This will:
- Start Neo4j, PostgreSQL, and Ollama
- Auto-pull the Gemma 4 E4B model into Ollama (~9 GB first run)
- Seed the Knowledge Graph with 8 concepts, 4 skills, 6 modules, and 40+ relationships
- Seed a demo user and learning path in PostgreSQL
- Start all 7 backend services + API Gateway
- Start the React frontend

> ⏳ First run takes longer due to the ~9 GB model download. Subsequent starts are fast since the model is cached in the `ollama_data` volume.

### 3. Open the app

| URL | What |
|-----|------|
| **http://localhost:3000** | Frontend UI |
| **http://localhost:8000** | API Gateway |
| **http://localhost:8000/docs** | Gateway API docs (Swagger) |
| **http://localhost:7474** | Neo4j Browser (neo4j / neuroforge_secret) |
| **http://localhost:11434** | Ollama API |

### 4. Try it out

1. **Dashboard** — See stats, quick actions, and your learning profile
2. **AI Mentor** — Ask "What is machine learning?" or "Explain neural networks"
3. **Concepts** — Browse the knowledge graph, see prerequisites and related concepts
4. **Learning Paths** — Enroll in "AI Foundations", complete modules, track progress

---

## 📡 API Quick Reference

All endpoints are accessible through the API Gateway at `http://localhost:8000/api/v1/`.

### User Service
```
POST /api/v1/users/register      — Register a new user
POST /api/v1/users/login         — Login, get JWT token
GET  /api/v1/users/{user_id}     — Get user profile
PUT  /api/v1/users/{user_id}     — Update profile
```

### Knowledge Graph
```
GET  /api/v1/concepts                          — List concepts (filter by domain, difficulty)
GET  /api/v1/concepts/{id}                     — Get concept details
GET  /api/v1/concepts/{id}/prerequisites       — Get prerequisites
GET  /api/v1/concepts/{id}/related             — Get related concepts
GET  /api/v1/concepts/{id}/modules             — Get teaching modules
GET  /api/v1/skills                            — List skills
GET  /api/v1/modules                           — List content modules
```

### AI Mentor
```
POST /api/v1/mentor/query        — Send a question to the AI Mentor (Gemma 4 E4B)
GET  /api/v1/mentor/history/{id} — Get conversation history
```

### Learning Pathways
```
GET  /api/v1/paths                                    — List learning paths
GET  /api/v1/paths/{path_id}                          — Get path details
POST /api/v1/users/{uid}/paths/{pid}/enroll           — Enroll in a path
PUT  /api/v1/users/{uid}/paths/{pid}/progress         — Update progress
GET  /api/v1/users/{uid}/paths/{pid}/enrollment       — Get enrollment status
```

### Cognitive Profiling
```
POST /api/v1/profiling/interactions              — Log interaction event
GET  /api/v1/profiling/users/{id}/summary        — Get cognitive profile
GET  /api/v1/profiling/users/{id}/heatmap        — Get behavioral heatmap
```

### Content Delivery
```
GET  /api/v1/content/{module_id}  — Get module content (HTML, quiz data)
GET  /api/v1/content              — List all available content
```

---

## 📂 Project Structure

```
NeuroForge-/
├── docker-compose.yml              # Full orchestration (incl. Ollama)
├── .env.example                    # Environment template (no API keys)
├── .gitignore
├── frontend/                       # React SPA
│   ├── Dockerfile
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── App.js                  # Router + layout
│       ├── App.css                 # Global dark theme
│       └── pages/
│           ├── Dashboard.js        # Stats, actions, profile
│           ├── MentorChat.js       # AI chat with personas (Gemma 4 E4B)
│           ├── ConceptBrowser.js   # KG explorer
│           └── LearningPath.js     # Path enrollment + progress
├── services/
│   ├── api_gateway/                # Unified API proxy
│   ├── user_service/               # Auth + profiles (PostgreSQL)
│   ├── knowledge_graph_service/    # Concepts, skills (Neo4j)
│   ├── ai_mentor_service/          # Gemma 4 E4B + KG integration (Ollama)
│   ├── cognitive_profiling_service/# Interaction logging (mock)
│   ├── content_delivery_service/   # Module content (mock)
│   └── learning_pathway_service/   # Paths + progress (PostgreSQL)
├── neo4j/seed/                     # Graph seed script
│   ├── Dockerfile
│   └── seed.py                     # 8 concepts, 4 skills, 6 modules, 40+ rels
└── docs/                           # Design documentation
    ├── neuroforge_architecture.md
    ├── neuroforge_api_design.md
    ├── neuroforge_poc_definition.md
    ├── neuroforge_neo4j_datamodel.md
    ├── neuroforge_ai_mentor_scaffolding.md
    ├── neuroforge_cognitive_profiling_design.md
    ├── neuroforge_blockchain_credentialing_design.md
    └── neuroforge_security_privacy_framework.md
```

---

## 🧪 PoC Scope & Next Steps

### What's implemented (PoC)
- ✅ Full microservices architecture with Docker Compose
- ✅ **Local LLM** — Gemma 4 E4B via Ollama (no cloud API keys)
- ✅ Neo4j Knowledge Graph with 8 concepts, 4 skills, 6 modules, 40+ relationships
- ✅ AI Mentor with KG context injection and 4 personas (Socratic, Coach, Expert, Adaptive)
- ✅ User registration/auth with JWT
- ✅ Learning pathway enrollment and progress tracking
- ✅ Cognitive profiling interaction logging with mock heatmaps
- ✅ React frontend with dark theme UI (Dashboard, Chat, Concept Browser, Paths)
- ✅ API Gateway with unified routing

### Future roadmap
- 🔲 Blockchain credentialing (Polygon PoS, ERC-721 NFT certificates)
- 🔲 Real PyTorch models for cognitive profiling and behavioral heatmapping
- 🔲 Vector database (ChromaDB/Weaviate) for AI Mentor long-term memory
- 🔲 Content CDN integration and rich media delivery
- 🔲 Real-time WebSocket support for live tutoring sessions
- 🔲 RBAC with granular permissions
- 🔲 GDPR/FERPA compliance module
- 🔲 Assessment engine with adaptive question difficulty
- 🔲 Production deployment (Kubernetes, CI/CD, monitoring)
- 🔲 Fine-tune Gemma on domain-specific educational content

---

## 📜 License

See [LICENSE](LICENSE) for details.
