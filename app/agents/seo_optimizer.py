from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import SEOMetadata
import json
import re

settings = get_settings()


def build_seo_chain():
    """Build a LangChain chain for SEO analysis and metadata generation."""

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.1,  # Very low — SEO metadata needs to be precise
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert SEO strategist.
Your job is to analyze blog post content and generate optimized metadata.

Rules for meta title:
- Between 50-60 characters exactly
- Include the focus keyword near the beginning
- Make it compelling and click-worthy
- Do not use clickbait

Rules for meta description:
- Between 150-160 characters exactly
- Summarize the post value clearly
- Include the focus keyword naturally
- End with a subtle call to action

Rules for slug:
- All lowercase
- Words separated by hyphens
- No special characters
- Maximum 5-6 words

Return ONLY a raw JSON object. No markdown, no backticks, nothing else.
Fields: meta_title, meta_description, slug, focus_keyword"""),
        ("human", """Analyze this blog post and generate SEO metadata.

Topic: {topic}
Primary keywords: {primary_keywords}
Content preview (first 500 chars): {content_preview}

Return the JSON object now."""),
    ])

    return prompt | llm


async def generate_seo_metadata(
    topic: str,
    primary_keywords: list,
    content: str,
) -> SEOMetadata:
    """Generate SEO metadata for the drafted blog post."""

    chain = build_seo_chain()

    result = await chain.ainvoke({
        "topic": topic,
        "primary_keywords": ", ".join(primary_keywords),
        "content_preview": content[:500],
    })

    raw = result.content if hasattr(result, 'content') else str(result)

    start = raw.find("{")
    end = raw.rfind("}") + 1
    json_str = raw[start:end]
    data = json.loads(json_str)

    return SEOMetadata(**data)


def score_seo(
    content: str,
    primary_keywords: list,
    meta_title: str,
    meta_description: str,
    word_count: int,
) -> tuple[int, list[str]]:
    """
    Score the SEO quality of the post and return suggestions.
    Returns a tuple of (score, suggestions).
    """
    score = 100
    suggestions = []

    # Word count check
    if word_count < 800:
        score -= 20
        suggestions.append("Post is too short. Aim for at least 800 words for SEO value.")
    elif word_count < 1200:
        score -= 10
        suggestions.append("Consider expanding to 1200+ words for better ranking potential.")

    # Keyword in first 100 words
    first_100 = " ".join(content.split()[:100]).lower()
    focus_keyword = primary_keywords[0].lower() if primary_keywords else ""
    if focus_keyword and focus_keyword not in first_100:
        score -= 15
        suggestions.append(f"Include the focus keyword '{primary_keywords[0]}' in the first 100 words.")

    # Meta title length
    if len(meta_title) < 50 or len(meta_title) > 60:
        score -= 10
        suggestions.append(f"Meta title is {len(meta_title)} chars. Keep it between 50-60 characters.")

    # Meta description length
    if len(meta_description) < 150 or len(meta_description) > 160:
        score -= 10
        suggestions.append(f"Meta description is {len(meta_description)} chars. Keep it between 150-160 characters.")

    # Keyword in meta title
    if focus_keyword and focus_keyword not in meta_title.lower():
        score -= 10
        suggestions.append(f"Include the focus keyword '{primary_keywords[0]}' in your meta title.")

    # H2 headings present
    h2_count = content.count("\n## ")
    if h2_count < 3:
        score -= 10
        suggestions.append("Add more H2 headings (aim for at least 3) to improve structure.")

    # Internal suggestion — keyword density
    keyword_count = content.lower().count(focus_keyword) if focus_keyword else 0
    density = (keyword_count / word_count * 100) if word_count > 0 else 0
    if density < 0.5:
        score -= 5
        suggestions.append(f"Focus keyword density is low ({density:.1f}%). Aim for 0.5-1.5%.")
    elif density > 3.0:
        score -= 10
        suggestions.append(f"Focus keyword density is too high ({density:.1f}%). Reduce to avoid keyword stuffing.")

    if not suggestions:
        suggestions.append("Great SEO! No major issues found.")

    return max(0, score), suggestions
