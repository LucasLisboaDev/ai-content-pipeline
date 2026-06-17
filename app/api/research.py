from fastapi import APIRouter, HTTPException
from app.core.models import ResearchBriefRequest, ResearchBrief
from app.agents.research_brief import generate_research_brief
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["Research Brief"])


@router.post("/brief", response_model=ResearchBrief)
async def generate_brief_endpoint(request: ResearchBriefRequest) -> ResearchBrief:
    """
    Research a topic and generate a structured content brief.

    - **topic**: The blog post topic to research (e.g. 'Top Strategies for Winning Your First BJJ Competition')
    - **target_audience**: Who the content is for (e.g. 'BJJ beginners', 'AI engineers')
    """
    try:
        logger.info(f"Generating research brief for topic: {request.topic}")
        result = await generate_research_brief(
            topic=request.topic,
            target_audience=request.target_audience,
        )
        return result
    except Exception as e:
        logger.error(f"Research brief generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research brief generation failed: {str(e)}")
