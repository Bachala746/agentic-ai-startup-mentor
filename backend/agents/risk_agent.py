import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import StartupState


load_dotenv()


class RiskAnalysis(BaseModel):
    market_risks: list[str] = Field(
        description="Important market-related risks"
    )
    financial_risks: list[str] = Field(
        description="Important financial risks"
    )
    product_technical_risks: list[str] = Field(
        description="Product and technical risks"
    )
    customer_adoption_risks: list[str] = Field(
        description="Customer and adoption risks"
    )
    implementation_challenges: list[str] = Field(
        description="Possible implementation challenges"
    )
    mitigation_strategies: list[str] = Field(
        description="Practical ways to reduce the identified risks"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


structured_llm = llm.with_structured_output(RiskAnalysis)


def risk_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}
    market_analysis = state.get("market_analysis") or {}
    financial_analysis = state.get("financial_analysis") or {}

    prompt = f"""
You are the Risk Agent in an AI Personalized Startup Mentor.

Analyze the risks and challenges of the startup.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Market Agent Analysis:
{market_analysis}

Finance Agent Analysis:
{financial_analysis}

Analyze:

1. Market risks
2. Financial risks
3. Product and technical risks
4. Customer/adoption risks
5. Implementation challenges
6. Practical mitigation strategies

Personalize the analysis using the founder's:
- Skills
- Experience
- Budget
- Goals

Do not invent precise statistics or unsupported facts.
Keep the analysis practical and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "risk_analysis": result.model_dump()
    }