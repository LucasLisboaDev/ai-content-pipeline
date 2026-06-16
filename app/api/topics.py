from fastapi import APIRouter, HTTPException
from app.core.models import TopicDiscoveryRequest, TopicDiscoveryResponse
from app.agents.topic_discovery import discover_topics
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topics", tags=["Topic Discovery"])


@router.post("/discover", response_model=TopicDiscoveryResponse)
async def discover_topics_endpoint(request: TopicDiscoveryRequest) -> TopicDiscoveryResponse:
    """
    Discover high-value blog post topics for a given niche.

    - **niche**: The niche or seed keyword (e.g. 'BJJ', 'AI engineering', 'SaaS marketing')
    - **num_topics**: Number of topics to return (1-10, default 5)
    """
    try:
        logger.info(f"Discovering topics for niche: {request.niche}")
        result = await discover_topics(
            niche=request.niche,
            num_topics=request.num_topics,
        )
        return result
    except Exception as e:
        logger.error(f"Topic discovery failed: {e}")
        raise HTTPException(status_code=500, detail=f"Topic discovery failed: {str(e)}")
