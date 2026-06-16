from pydantic import BaseModel, Field
from typing import List


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
