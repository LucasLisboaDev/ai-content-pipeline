from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_settings
from app.core.models import DraftRequest
import re

settings = get_settings()


def build_drafting_chain():
    """Build a LangChain chain (not agent) for drafting blog posts."""

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a world-class content writer and SEO specialist.
Your job is to write engaging, informative, and SEO-optimized blog posts.

Writing guidelines:
- Write in a conversational but authoritative tone
- Use the primary keywords naturally throughout — never force them
- Include the focus keyword in the first 100 words
- Write compelling section introductions that hook the reader
- Use concrete examples, actionable advice, and specific details
- Avoid fluff — every sentence must add value
- End with a strong conclusion and clear call to action
- Format in clean markdown with proper H2 and H3 headings"""),
        ("human", """Write a full blog post using the details below.

Topic: {topic}
Target audience: {target_audience}
Content angle: {content_angle}
Primary keywords: {primary_keywords}
Secondary keywords: {secondary_keywords}
Target word count: {word_count} words

Outline to follow:
{outline}

Write the complete blog post in markdown. Include a compelling H1 title at the top.
Do not include meta title or description — just the post content."""),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain


async def draft_post(request: DraftRequest) -> str:
    """Generate a full blog post draft from the research brief."""

    chain = build_drafting_chain()

    # Format outline as readable text for the prompt
    outline_text = ""
    for section in request.content_outline:
        outline_text += f"\n## {section.heading}\n"
        for point in section.key_points:
            outline_text += f"- {point}\n"

    result = await chain.ainvoke({
        "topic": request.topic,
        "target_audience": request.target_audience,
        "content_angle": request.content_angle,
        "primary_keywords": ", ".join(request.primary_keywords),
        "secondary_keywords": ", ".join(request.secondary_keywords),
        "word_count": request.recommended_word_count,
        "outline": outline_text,
    })

    return result


def count_words(text: str) -> int:
    """Count words in the markdown content."""
    # Strip markdown syntax for accurate count
    clean = re.sub(r'[#*`\[\]()>-]', '', text)
    return len(clean.split())


def calculate_keyword_density(content: str, keywords: list) -> dict:
    """Count occurrences of each keyword in the content."""
    content_lower = content.lower()
    density = {}
    for keyword in keywords:
        count = content_lower.count(keyword.lower())
        density[keyword] = count
    return density
