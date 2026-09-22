import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import StartupState


load_dotenv()


class MarketAnalysis(BaseModel):
    target_customers: list[str] = Field(
        description="Potential target customer groups"
    )
    customer_problem: str = Field(
        description="Main problem or need of the target customers"
    )
    market_demand: str = Field(
        description="Simple assessment of potential market demand"
    )
    opportunities: list[str] = Field(
        description="Potential market opportunities"
    )
    competitors: list[str] = Field(
        description="Known competitors or alternative solutions if information is available"
    )
    market_gaps: list[str] = Field(
        description="Potential gaps or underserved areas in the market"
    )
    market_insights: list[str] = Field(
        description="Concise and practical market insights"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


structured_llm = llm.with_structured_output(MarketAnalysis)


def market_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}

    prompt = f"""
You are the Market Agent in an AI Personalized Startup Mentor.

Analyze the startup idea using the founder information.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Analyze:

1. Target customers
2. Customer problem or need
3. Potential market demand
4. Market opportunities
5. Competitors or alternative solutions, only when information is available
6. Potential market gaps
7. Concise practical market insights

Personalize the analysis using the founder's:
- Skills
- Interests
- Experience
- Budget
- Goals

Do not invent precise market statistics or unsupported facts.
Keep the analysis practical and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "market_analysis": result.model_dump()
    }