# AI Content Pipeline

An autonomous content engine that discovers trending topics, researches them using live web search, drafts SEO-optimized blog posts, and publishes them to a CMS — fully orchestrated and scheduled with zero manual intervention.

**Live demo post:** https://thesupercreator.ghost.io/brazilian-jiu-jitsu-misconceptions/

---

## What It Does

This system takes a niche (e.g. "Brazilian Jiu-Jitsu") and autonomously:

1. **Discovers** high-value blog topics using a LangChain agent with real-time web search
2. **Researches** the best topic in depth — competitor gaps, keywords, content outline
3. **Drafts** a full SEO-optimized blog post using GPT-4o
4. **Publishes** the post as a draft to Ghost CMS via the Admin API
5. **Notifies** via email when a new post is live

The entire flow runs on a schedule, orchestrated by n8n, calling a FastAPI backend deployed on Railway.

---

## Architecture

```
┌─────────────────┐
│ n8n Scheduler    │  Triggers every 2 days
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (Railway)                │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                │
│  │ Topic Agent  │───▶│Research Agent│                │
│  │ (LangChain + │    │ (LangChain + │                │
│  │  Tavily)     │    │  Tavily)     │                │
│  └──────────────┘    └──────┬───────┘                │
│                              │                         │
│                              ▼                         │
│                      ┌──────────────┐                │
│                      │Drafting Chain│                │
│                      │   (GPT-4o)   │                │
│                      └──────┬───────┘                │
│                              │                         │
│                              ▼                         │
│                      ┌──────────────┐                │
│                      │ SEO Scorer   │                │
│                      │  (Python)    │                │
│                      └──────┬───────┘                │
│                              │                         │
│                              ▼                         │
│                      ┌──────────────┐                │
│                      │Ghost Publisher│                │
│                      │  (JWT Auth)   │                │
│                      └──────┬───────┘                │
└──────────────────────────────┼─────────────────────────┘
                               │
                               ▼
                      ┌──────────────┐
                      │  Ghost CMS    │
                      │ (Live Post)   │
                      └──────────────┘
                               │
                               ▼
                      ┌──────────────┐
                      │Email Notify   │
                      │  (n8n→Gmail)  │
                      └──────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Agent orchestration | LangChain | Tool-calling agents for autonomous research |
| Search | Tavily | LLM-optimized real-time web search |
| Generation | GPT-4o | Drafting and structured reasoning |
| API | FastAPI | Async-native, auto-validated, auto-documented |
| Validation | Pydantic | Type-safe contracts between every pipeline stage |
| Deployment | Railway | Public, persistent backend hosting |
| Workflow orchestration | n8n | Visual scheduling, chaining, and monitoring |
| CMS | Ghost | Clean Admin API for programmatic publishing |
| Auth | JWT (PyJWT) | Secure, short-lived Ghost API authentication |

---

## API Endpoints

```
POST /api/v1/topics/discover     → Discover blog topics for a niche
POST /api/v1/research/brief      → Generate a research brief for a topic
POST /api/v1/draft/generate      → Draft and SEO-score a full blog post
POST /api/v1/publish/ghost       → Publish a draft to Ghost CMS
GET  /health                     → Health check
```

Full interactive API docs available at `/docs` once running.

---

## Engineering Decisions Worth Noting

**Agents vs. Chains** — Topic discovery and research use autonomous LangChain agents because they require tool use and multi-step reasoning over live search results. Drafting and SEO metadata use simple LCEL chains because all required information is already available — no tool calls needed, just generation.

**Temperature tuning per task** — Research and metadata generation run at low temperature (0.1–0.2) for consistency and factual accuracy. Drafting runs at 0.7 for natural, engaging prose.

**Deterministic SEO scoring** — The SEO score is calculated in pure Python, not by an LLM. Character counts and keyword density are measurable facts, not reasoning tasks — using an LLM for arithmetic would be slower, costlier, and less reliable.

**Draft-first publishing** — Posts publish to Ghost as drafts by default, never live. This keeps a human in the loop for final review before anything goes public — a deliberate responsible-AI design choice.

**Separation of concerns** — Each phase of the pipeline is its own router, its own agent module, and its own Pydantic models. Any single component can be modified, tested, or replaced without touching the others.

---

## Setup

```bash
git clone https://github.com/LucasLisboaDev/ai-content-pipeline.git
cd ai-content-pipeline
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI, Tavily, and Ghost API keys to .env
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` to test endpoints interactively.

---

## Roadmap

- [x] Phase 1 — Topic Discovery Agent
- [x] Phase 2 — Research Brief Agent
- [x] Phase 3 — Drafting & SEO Optimization
- [x] Phase 4 — Ghost Publishing Integration
- [x] Phase 5 — n8n Scheduling & Cloud Deployment
- [x] Phase 6 — Documentation & Portfolio Packaging

---

## Author

Built by [Lucas Lisboa](https://portfolio-lucas-henna.vercel.app) — AI Engineer focused on agentic systems and production LLM pipelines.