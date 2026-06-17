from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import ResearchBrief, OutlineSection
import json

settings = get_settings()


def build_research_agent() -> AgentExecutor:
    """Build the LangChain agent for deep topic research and brief generation."""

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )

    search_tool = TavilySearchResults(
        max_results=5,
        tavily_api_key=settings.tavily_api_key,
    )

    tools = [search_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior content strategist and SEO researcher.
Your job is to deeply research a blog post topic and produce a comprehensive content brief.

When given a topic and target audience:
1. Search for the top-ranking content on this topic to understand what already exists
2. Search for common questions and pain points around this topic
3. Search for recent news, data, or angles that competitors might be missing
4. Identify keyword opportunities and content gaps

After thorough research, produce ONLY a raw JSON object (no markdown, no backticks, no explanation).
Start your response with {{ and end with }}.

The JSON must have exactly these fields:
- topic: string
- target_audience: string
- primary_keywords: array of 3-5 main SEO keywords
- secondary_keywords: array of 5-8 supporting keywords
- competitor_gaps: array of 3-5 angles or subtopics competitors are missing
- content_outline: array of sections, each with "heading" (string) and "key_points" (array of strings)
- recommended_word_count: integer between 1000 and 3000
- key_sources: array of URLs found during research that are most valuable
- content_angle: a single sentence describing the unique angle that makes this post stand out"""),
        ("human", "Research this topic and create a content brief.\nTopic: {topic}\nTarget audience: {target_audience}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=6,
        return_intermediate_steps=False,
    )


async def generate_research_brief(topic: str, target_audience: str) -> ResearchBrief:
    """Run the research agent and return a structured content brief."""

    agent_executor = build_research_agent()

    result = await agent_executor.ainvoke({
        "topic": topic,
        "target_audience": target_audience,
    })

    raw_output = result.get("output", "")

    # Extract JSON object robustly — find first { to last }
    start = raw_output.find("{")
    end = raw_output.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in agent output: {raw_output}")

    json_str = raw_output[start:end]
    brief_data = json.loads(json_str)

    # Parse nested outline sections
    outline = [
        OutlineSection(**section)
        for section in brief_data.get("content_outline", [])
    ]
    brief_data["content_outline"] = outline

    return ResearchBrief(**brief_data)
