from pydantic import BaseModel, Field
from typing import List


# ── Phase 1 Models ────────────────────────────────────────────────────────────

class TopicDiscoveryRequest(BaseModel):
    niche: str = Field(..., description="The niche or seed keyword to discover topics for")
    num_topics: int = Field(default=5, ge=1, le=10, description="Number of topics to return")


class ScoredTopic(BaseModel):
    title: str = Field(..., description="The blog post topic title")
    relevance_score: float = Field(..., ge=0, le=10, description="Relevance score from 0-10")
    reasoning: str = Field(..., description="Why this topic is valuable for the niche")
    target_keywords: List[str] = Field(..., description="Primary keywords to target")
    estimated_difficulty: str = Field(..., description="Low / Medium / High competition estimate")


class TopicDiscoveryResponse(BaseModel):
    niche: str
    topics: List[ScoredTopic]
    total_found: int


# ── Phase 2 Models ────────────────────────────────────────────────────────────

class ResearchBriefRequest(BaseModel):
    topic: str = Field(..., description="The blog post topic to research")
    target_audience: str = Field(
        default="general audience",
        description="Who the content is written for (e.g. 'BJJ beginners', 'AI engineers')"
    )


class OutlineSection(BaseModel):
    heading: str = Field(..., description="Section heading (H2 or H3)")
    key_points: List[str] = Field(..., description="Key points to cover in this section")


class ResearchBrief(BaseModel):
    topic: str
    target_audience: str
    primary_keywords: List[str] = Field(..., description="Main keywords to target for SEO")
    secondary_keywords: List[str] = Field(..., description="Supporting/LSI keywords")
    competitor_gaps: List[str] = Field(..., description="Angles competitors are missing")
    content_outline: List[OutlineSection] = Field(..., description="Full structured outline")
    recommended_word_count: int = Field(..., description="Suggested word count for the post")
    key_sources: List[str] = Field(..., description="URLs of valuable sources found during research")
    content_angle: str = Field(..., description="The unique angle that makes this post stand out")
