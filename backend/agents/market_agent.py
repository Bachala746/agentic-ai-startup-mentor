import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

from .state import StartupState


load_dotenv()


class CompetitorAlternative(BaseModel):
    name: str = Field(
        description=(
            "Name of a real competitor, company, product, platform, "
            "or alternative solution relevant to the startup idea"
        )
    )

    description: str = Field(
        description=(
            "Short 1-2 sentence explanation of what this competitor "
            "or alternative does"
        )
    )


class MarketAnalysis(BaseModel):
    target_customers: list[str] = Field(
        description=(
            "Potential target customer groups based on the startup idea "
            "and current web information"
        )
    )

    customer_problem: str = Field(
        description="Main problem or need of the target customers"
    )

    market_demand: str = Field(
        description=(
            "Assessment of potential market demand using available "
            "current web information"
        )
    )

    opportunities: list[str] = Field(
        description=(
            "Potential market opportunities supported by current "
            "information"
        )
    )

    competitors_or_alternatives: list[CompetitorAlternative] = Field(
        description=(
            "Real competitors or alternative solutions found from "
            "the current web research. Each item must contain both "
            "a name and a short description."
        )
    )

    market_gaps: list[str] = Field(
        description=(
            "Potential gaps or underserved areas identified from "
            "the current information"
        )
    )

    market_insights: list[str] = Field(
        description=(
            "Concise and practical market insights based on current "
            "web information"
        )
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


structured_llm = llm.with_structured_output(MarketAnalysis)


def search_current_market_information(startup_idea: str):
    """
    Search the web for current information related to the startup idea.
    """

    queries = [
        {
            "category": "Market Trends",
            "query": f"{startup_idea} market trends 2026",
        },
        {
            "category": "Competitors & Alternatives",
            "query": (
                f"{startup_idea} competitors companies "
                f"products platforms alternatives 2026"
            ),
        },
        {
            "category": "Recent Developments",
            "query": (
                f"{startup_idea} recent developments "
                f"technology companies 2026"
            ),
        },
    ]

    all_results = []

    for search in queries:
        try:
            results = DDGS().text(
                search["query"],
                max_results=5,
            )

            for result in results:
                all_results.append(
                    {
                        "category": search["category"],
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    }
                )

        except Exception as error:
            print(
                f"Web search failed for '{search['query']}': {error}"
            )

    # Remove duplicate URLs
    unique_results = []
    seen_urls = set()

    for result in all_results:
        url = result.get("url", "").strip()

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    return unique_results[:15]


def market_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}

    # Get current information from the web
    web_results = search_current_market_information(startup_idea)

    web_information_parts = []

    for index, result in enumerate(web_results, start=1):
        web_information_parts.append(
            f"""
SOURCE {index}
Category: {result["category"]}
Title: {result["title"]}
URL: {result["url"]}
Information: {result["snippet"]}
"""
        )

    web_information = "\n".join(web_information_parts)

    prompt = f"""
You are the Market Agent in an AI Personalized Startup Mentor.

Your job is to analyze the startup idea using BOTH:

1. The user's profile
2. Current information retrieved from the web

IMPORTANT:
The web information below was retrieved during the current request.
Use it as current market evidence.

STARTUP IDEA:
{startup_idea}

USER PROFILE:
{founder_profile}

CURRENT WEB INFORMATION:
{web_information}

Analyze the following:

1. Target customers
2. Customer problem or need
3. Potential market demand
4. Market opportunities
5. Real competitors or alternative solutions
6. Potential market gaps
7. Practical market insights

COMPETITORS / ALTERNATIVES REQUIREMENT:

For competitors_or_alternatives:

- Find REAL companies, products, platforms, or alternative solutions.
- Prefer names found in the current web results.
- Do not invent competitors.
- Give both the competitor name and a short description.
- The description must explain what the competitor or alternative does.
- Give several relevant competitors/alternatives when the web results
  contain enough information.
- If a result mentions a company or product that is clearly relevant,
  consider it as a possible competitor or alternative.
- Do not return only names.
- Every competitor must have:
    name
    description

MARKET ANALYSIS REQUIREMENTS:

Use the current web information to identify:

- Real companies or products
- Current market trends
- Recent developments
- Existing competitors
- Current opportunities
- Current customer needs
- Market gaps

IMPORTANT RULES:

- Prefer current web information over unsupported assumptions.
- Do not invent companies.
- Do not invent statistics.
- Do not invent prices.
- Do not invent market numbers.
- Do not create precise statistics unless supported by the web results.
- Do not treat every web result as automatically trustworthy.
- Use web results as evidence.
- If current information is limited, clearly use general reasoning.
- Personalize the analysis using the user's:
  - Skills
  - Interests
  - Experience
  - Budget
  - Goals

Keep the output practical, clear, and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "market_analysis": result.model_dump(),
        "web_sources": web_results,
    }