from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.topics import router as topics_router
from app.api.research import router as research_router
from app.api.draft import router as draft_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="AI Content Pipeline",
    description="Autonomous content engine powered by LangChain and GPT-4o",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")
app.include_router(draft_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.3.0", "phase": 3}
