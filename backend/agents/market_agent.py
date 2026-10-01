import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

from .state import StartupState


load_dotenv()


# ============================================================
# COMPETITOR / ALTERNATIVE MODEL
# ============================================================

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


# ============================================================
# MARKET ANALYSIS MODEL
# ============================================================

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


# ============================================================
# GEMINI MODEL
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

structured_llm = llm.with_structured_output(MarketAnalysis)


# ============================================================
# WEB SEARCH
# ============================================================

def search_current_market_information(startup_idea: str):
    """
    Search current web information in three separate categories.

    Each category keeps its own results so that duplicate URLs
    between categories do not remove an entire category.
    """

    queries = [
        {
            "category": "Market Trends",
            "queries": [
                f"{startup_idea} market trends 2026",
                f"{startup_idea} industry trends 2026",
            ],
        },
        {
            "category": "Competitors & Alternatives",
            "queries": [
                f"{startup_idea} companies products solutions competitors",
            ],
        },
        {
            "category": "Competitors & Alternatives",
            "queries": [
                f"{startup_idea} similar companies alternative solutions",
            ],
        },
        {
            "category": "Competitors & Alternatives",
            "queries": [
                f"{startup_idea} leading companies technology providers",
            ],
        },
        {
            "category": "Recent Developments",
            "queries": [
                f"{startup_idea} latest news developments 2026",
                f"{startup_idea} recent technology developments 2026",
            ],
        },
    ]

    categorized_results = {
        "Market Trends": [],
        "Competitors & Alternatives": [],
        "Recent Developments": [],
    }

    # --------------------------------------------------------
    # Search each category independently
    # --------------------------------------------------------

    for search in queries:

        category = search["category"]

        for query in search["queries"]:

            try:
                results = DDGS().text(
                    query,
                    max_results=5,
                )

                for result in results:

                    title = result.get("title", "").strip()
                    url = result.get("href", "").strip()
                    snippet = result.get("body", "").strip()

                    if not url:
                        continue

                    categorized_results[category].append(
                        {
                            "category": category,
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                        }
                    )

            except Exception as error:
                print(
                    f"Web search failed for '{query}': {error}"
                )

    # --------------------------------------------------------
    # Remove duplicates INSIDE each category only
    # --------------------------------------------------------

    final_results = []

    for category, results in categorized_results.items():

        seen_urls = set()
        category_results = []

        for result in results:

            url = result["url"]

            if url in seen_urls:
                continue

            seen_urls.add(url)
            category_results.append(result)

            # Keep maximum 5 results per category
            if len(category_results) >= 5:
                break

        final_results.extend(category_results)

    print(
        "Web research results:",
        {
            category: len(results)
            for category, results in categorized_results.items()
        },
    )

    return final_results


# ============================================================
# MARKET AGENT
# ============================================================

def market_agent(state: StartupState):

    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}

    # --------------------------------------------------------
    # Get current information from the web
    # --------------------------------------------------------

    web_results = search_current_market_information(
        startup_idea
    )

    # --------------------------------------------------------
    # Prepare web information for Gemini
    # --------------------------------------------------------

    web_information_parts = []

    for index, result in enumerate(
        web_results,
        start=1,
    ):

        web_information_parts.append(
            f"""
SOURCE {index}

Category:
{result["category"]}

Title:
{result["title"]}

URL:
{result["url"]}

Information:
{result["snippet"]}
"""
        )

    web_information = "\n".join(
        web_information_parts
    )

    # --------------------------------------------------------
    # Gemini Market Agent Prompt
    # --------------------------------------------------------

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


============================================================
COMPETITORS / ALTERNATIVES
============================================================

For competitors_or_alternatives:

- Find REAL companies, products, platforms, or alternative solutions.
- Prefer names that appear in the current web research.
- Do not invent competitors.
- Do not create fictional company names.
- Give both the competitor name and description.
- Explain briefly what each competitor or alternative does.
- Include several relevant competitors when enough web evidence exists.
- If the web research contains a clearly relevant company or product,
  consider it as a possible competitor or alternative.
- Every competitor must contain:
    name
    description


============================================================
CURRENT WEB RESEARCH
============================================================

Use the web research to identify:

- Current market trends
- Real companies and products
- Competitors and alternatives
- Recent developments
- Current opportunities
- Customer needs
- Market gaps


============================================================
IMPORTANT RULES
============================================================

- Prefer current web information over unsupported assumptions.
- Do not invent companies.
- Do not invent statistics.
- Do not invent prices.
- Do not invent market numbers.
- Do not create precise statistics unless supported by the web results.
- Do not treat every web result as automatically trustworthy.
- Use web results as evidence.
- If current information is limited, clearly use general reasoning.
- Do not claim that a company is a competitor unless it is relevant
  to the startup idea.

Personalize the analysis using the user's:

- Skills
- Interests
- Experience
- Budget
- Goals

Keep the output practical, clear, and easy to understand.
"""

    # --------------------------------------------------------
    # Generate structured market analysis
    # --------------------------------------------------------

    result = structured_llm.invoke(prompt)

    # --------------------------------------------------------
    # Return both AI analysis and actual web sources
    # --------------------------------------------------------

    return {
        "market_analysis": result.model_dump(),
        "web_sources": web_results,
    }