from pydantic import BaseModel, Field
from typing import List, Optional


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
        description="Who the content is written for"
    )


class OutlineSection(BaseModel):
    heading: str = Field(..., description="Section heading (H2 or H3)")
    key_points: List[str] = Field(..., description="Key points to cover in this section")


class ResearchBrief(BaseModel):
    topic: str
    target_audience: str
    primary_keywords: List[str]
    secondary_keywords: List[str]
    competitor_gaps: List[str]
    content_outline: List[OutlineSection]
    recommended_word_count: int
    key_sources: List[str]
    content_angle: str


# ── Phase 3 Models ────────────────────────────────────────────────────────────

class DraftRequest(BaseModel):
    topic: str = Field(..., description="The blog post topic")
    target_audience: str = Field(default="general audience")
    primary_keywords: List[str] = Field(..., description="Main SEO keywords to target")
    secondary_keywords: List[str] = Field(default=[], description="Supporting keywords")
    content_outline: List[OutlineSection] = Field(..., description="Structured outline from Phase 2")
    content_angle: str = Field(..., description="Unique angle for this post")
    recommended_word_count: int = Field(default=1500)


class SEOMetadata(BaseModel):
    meta_title: str = Field(..., description="SEO meta title (50-60 characters)")
    meta_description: str = Field(..., description="SEO meta description (150-160 characters)")
    slug: str = Field(..., description="URL-friendly slug for the post")
    focus_keyword: str = Field(..., description="Primary keyword this post targets")


class DraftResponse(BaseModel):
    topic: str
    markdown_content: str = Field(..., description="Full blog post in markdown format")
    seo_metadata: SEOMetadata
    word_count: int
    keyword_density: dict = Field(..., description="Keyword occurrence counts in the draft")
    seo_score: int = Field(..., ge=0, le=100, description="SEO quality score 0-100")
    seo_suggestions: List[str] = Field(..., description="Actionable SEO improvement suggestions")


# ── Phase 4 Models ────────────────────────────────────────────────────────────

class PublishRequest(BaseModel):
    topic: str = Field(..., description="The blog post topic")
    markdown_content: str = Field(..., description="Full blog post markdown from Phase 3")
    seo_metadata: "SEOMetadata" = Field(..., description="SEO metadata from Phase 3")
    publish_status: str = Field(
        default="draft",
        description="Ghost post status: 'draft' or 'published'"
    )
    tags: List[str] = Field(default=[], description="Tags to attach to the post in Ghost")


class PublishResponse(BaseModel):
    success: bool
    ghost_post_id: str = Field(..., description="The ID Ghost assigned to the post")
    ghost_post_url: str = Field(..., description="The URL of the post in Ghost")
    status: str = Field(..., description="Post status in Ghost: draft or published")
    title: str = Field(..., description="The post title as published")
