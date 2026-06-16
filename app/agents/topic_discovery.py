from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.core.models import ScoredTopic, TopicDiscoveryResponse
import json

settings = get_settings()


def build_topic_discovery_agent() -> AgentExecutor:
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )

    search_tool = TavilySearchResults(
        max_results=5,
        tavily_api_key=settings.tavily_api_key,
    )

    tools = [search_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert content strategist and SEO specialist.
Your job is to discover high-value blog post topics for a given niche.

When given a niche or seed keyword:
1. Use the search tool to find trending topics, common questions, and content gaps
2. Analyze what types of content perform well
3. Identify keyword opportunities

CRITICAL: Your final response must be ONLY a raw JSON array. No markdown, no backticks, no explanation text before or after.
Start your response with [ and end with ]. Nothing else.

Each item in the array must have these exact fields:
- title: string
- relevance_score: float between 0 and 10
- reasoning: string explaining why this topic is valuable
- target_keywords: array of strings
- estimated_difficulty: must be exactly one of Low, Medium, or High"""),
        ("human", "Discover {num_topics} high-value blog post topics for this niche: {niche}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        return_intermediate_steps=False,
    )


async def discover_topics(niche: str, num_topics: int = 5) -> TopicDiscoveryResponse:
    agent_executor = build_topic_discovery_agent()

    result = await agent_executor.ainvoke({
        "niche": niche,
        "num_topics": num_topics,
    })

    raw_output = result.get("output", "")

    # Extract JSON array robustly — find first [ to last ]
    start = raw_output.find("[")
    end = raw_output.rfind("]") + 1

    if start == -1 or end == 0:
        raise ValueError(f"No JSON array found in agent output: {raw_output}")

    json_str = raw_output[start:end]
    topics_data = json.loads(json_str)
    topics = [ScoredTopic(**topic) for topic in topics_data]

    return TopicDiscoveryResponse(
        niche=niche,
        topics=topics,
        total_found=len(topics),
    )
