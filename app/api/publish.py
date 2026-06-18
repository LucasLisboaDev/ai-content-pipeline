from fastapi import APIRouter, HTTPException
from app.core.models import PublishRequest, PublishResponse
from app.agents.ghost_publisher import publish_to_ghost
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/publish", tags=["Ghost Publishing"])


@router.post("/ghost", response_model=PublishResponse)
async def publish_to_ghost_endpoint(request: PublishRequest) -> PublishResponse:
    """
    Publish a drafted blog post to Ghost CMS.

    - **markdown_content**: Full blog post markdown from Phase 3
    - **seo_metadata**: SEO metadata object from Phase 3
    - **publish_status**: 'draft' (default) or 'published'
    - **tags**: Optional list of tag names to attach to the post
    """
    try:
        logger.info(f"Publishing post to Ghost: {request.topic}")
        result = await publish_to_ghost(request)
        return result
    except Exception as e:
        logger.error(f"Ghost publishing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ghost publishing failed: {str(e)}")
