import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

from .state import StartupState

load_dotenv()


class FundingOpportunity(BaseModel):
    name: str = ""
    funding_type: str = ""
    funding_amount: str = ""
    eligibility: str = ""
    who_can_apply: str = ""
    startup_stage: str = ""
    usage: str = ""
    where_to_apply: str = ""
    application_website: str = ""
    application_steps: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    deadline: str = ""
    official_source: str = ""
    why_suitable: str = ""


class TeamRole(BaseModel):
    role: str = ""
    responsibilities: str = ""
    why_needed: str = ""
    skills: list[str] = Field(default_factory=list)
    priority: str = ""


class Competitor(BaseModel):
    name: str = ""
    product_service: str = ""
    target_customers: str = ""
    business_model: str = ""
    pricing: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    revenue: str = ""
    profit_loss: str = ""
    source: str = ""


class StartupIntelligenceReport(BaseModel):
    executive_summary: str = ""
    funding_opportunities: list[FundingOpportunity] = Field(default_factory=list)
    recommended_team_structure: list[TeamRole] = Field(default_factory=list)
    competitor_analysis: list[Competitor] = Field(default_factory=list)
    financial_information: list[str] = Field(default_factory=list)
    startup_vs_competitors: list[str] = Field(default_factory=list)
    important_recommendations: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

structured_llm = llm.with_structured_output(StartupIntelligenceReport)


def search_intelligence_information(startup_idea: str):
    queries = [
        f"{startup_idea} government funding schemes grants India startup",
        f"{startup_idea} startup grants seed funding incubators accelerators India",
        f"{startup_idea} competitors companies products India",
        f"{startup_idea} competitors pricing revenue financial results",
        f"{startup_idea} startup funding eligibility application",
    ]

    results = []

    for query in queries:
        try:
            search_results = DDGS().text(query, max_results=5)

            for item in search_results:
                url = item.get("href", "").strip()

                if url:
                    results.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("body", ""),
                    })

        except Exception as error:
            print(f"Intelligence search failed: {error}")

    unique = []
    seen = set()

    for result in results:
        if result["url"] not in seen:
            seen.add(result["url"])
            unique.append(result)

    return unique[:25]


def startup_intelligence_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}

    web_results = search_intelligence_information(startup_idea)

    web_information = "\n\n".join(
        f"SOURCE:\n"
        f"Title: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"Information: {item['snippet']}"
        for item in web_results
    )

    prompt = f"""
You are the Startup Intelligence Agent.

Analyze this startup idea using the user profile and CURRENT web research.

STARTUP IDEA:
{startup_idea}

USER PROFILE:
{founder_profile}

CURRENT WEB RESEARCH:
{web_information}

Your output must cover:

1. FUNDING
Find relevant government schemes, grants, seed funding, loans,
incubators and accelerators.

Never invent funding amounts, eligibility, deadlines,
application procedures or links.
Use only information supported by the web research.
If information is unavailable, say "Not verified".

2. COMPANY / TEAM
Recommend roles specifically for this startup.
Separate essential initial roles from later roles.

3. COMPETITORS
Identify real competitors or alternatives from the research.
Never invent companies.

4. FINANCIAL INFORMATION
Include pricing, revenue and profit/loss only when publicly
supported by the research.
Otherwise say "Not publicly verified".

5. STARTUP VS COMPETITORS
Give a simple practical comparison.

6. RECOMMENDATIONS
Give practical next steps for the founder.

7. SOURCES
Include URLs from the research that support the information.

IMPORTANT:
- Prefer official government and organization sources.
- Do not invent facts.
- Do not invent financial numbers.
- Clearly mark unverified information.
- Do not include maps or location analysis.
- Keep the result practical and structured.
"""

    result = structured_llm.invoke(prompt)

    return {
        "startup_intelligence": result.model_dump(),
    }