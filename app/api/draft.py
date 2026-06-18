from fastapi import APIRouter, HTTPException
from app.core.models import DraftRequest, DraftResponse
from app.agents.drafter import draft_post, count_words, calculate_keyword_density
from app.agents.seo_optimizer import generate_seo_metadata, score_seo
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/draft", tags=["Drafting & SEO"])


@router.post("/generate", response_model=DraftResponse)
async def generate_draft_endpoint(request: DraftRequest) -> DraftResponse:
    """
    Draft a full SEO-optimized blog post from a research brief.

    - **topic**: The blog post topic
    - **primary_keywords**: Main SEO keywords from Phase 2
    - **content_outline**: Structured outline from Phase 2
    - **content_angle**: Unique angle from Phase 2
    - **recommended_word_count**: Target word count from Phase 2
    """
    try:
        logger.info(f"Drafting post for topic: {request.topic}")

        # Step 1 — Draft the post
        markdown_content = await draft_post(request)
        logger.info("Draft complete. Running SEO optimization...")

        # Step 2 — Generate SEO metadata
        seo_metadata = await generate_seo_metadata(
            topic=request.topic,
            primary_keywords=request.primary_keywords,
            content=markdown_content,
        )

        # Step 3 — Analyze and score SEO
        word_count = count_words(markdown_content)
        keyword_density = calculate_keyword_density(
            markdown_content,
            request.primary_keywords + request.secondary_keywords,
        )
        seo_score, seo_suggestions = score_seo(
            content=markdown_content,
            primary_keywords=request.primary_keywords,
            meta_title=seo_metadata.meta_title,
            meta_description=seo_metadata.meta_description,
            word_count=word_count,
        )

        logger.info(f"SEO score: {seo_score}/100. Word count: {word_count}")

        return DraftResponse(
            topic=request.topic,
            markdown_content=markdown_content,
            seo_metadata=seo_metadata,
            word_count=word_count,
            keyword_density=keyword_density,
            seo_score=seo_score,
            seo_suggestions=seo_suggestions,
        )

    except Exception as e:
        logger.error(f"Draft generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Draft generation failed: {str(e)}")
