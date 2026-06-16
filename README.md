# AI Content Pipeline — Phase 1: Topic Discovery

An autonomous content engine powered by LangChain, GPT-4o, and Tavily search.

## Stack
- **FastAPI** — REST API backend
- **LangChain** — Agent orchestration
- **GPT-4o** — Language model
- **Tavily** — Real-time web search
- **Pydantic** — Data validation

## Project Structure
```
ai-content-pipeline/
├── app/
│   ├── agents/
│   │   └── topic_discovery.py   # LangChain topic discovery agent
│   ├── api/
│   │   └── topics.py            # FastAPI route for /topics/discover
│   ├── core/
│   │   ├── config.py            # Settings and env vars
│   │   └── models.py            # Pydantic data models
│   └── main.py                  # FastAPI app entry point
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

1. **Clone and install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Add your API keys to .env
```

Get your API keys:
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://app.tavily.com

3. **Run the server**
```bash
uvicorn app.main:app --reload
```

4. **Test the endpoint**
```bash
curl -X POST http://localhost:8000/api/v1/topics/discover \
  -H "Content-Type: application/json" \
  -d '{"niche": "Brazilian jiu-jitsu", "num_topics": 5}'
```

## API Reference

### POST /api/v1/topics/discover

Discover high-value blog post topics for a niche.

**Request body:**
```json
{
  "niche": "AI engineering",
  "num_topics": 5
}
```

**Response:**
```json
{
  "niche": "AI engineering",
  "total_found": 5,
  "topics": [
    {
      "title": "How to Build a Production RAG Pipeline in 2025",
      "relevance_score": 9.2,
      "reasoning": "High search volume, growing interest in production AI systems",
      "target_keywords": ["RAG pipeline", "production AI", "LangChain"],
      "estimated_difficulty": "Medium"
    }
  ]
}
```

### GET /health
Health check endpoint.

## Phases Roadmap
- [x] **Phase 1** — Topic Discovery Agent
- [ ] **Phase 2** — Research & Brief Generation
- [ ] **Phase 3** — Drafting & SEO Optimization
- [ ] **Phase 4** — Ghost Publishing Integration
- [ ] **Phase 5** — n8n Scheduling & Orchestration
- [ ] **Phase 6** — Polish & Portfolio Packaging
