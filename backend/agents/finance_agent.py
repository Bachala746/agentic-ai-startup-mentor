import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import StartupState


load_dotenv()


class FinancialAnalysis(BaseModel):
    financial_practicality: str = Field(
        description="Overall financial practicality of the startup"
    )
    expense_categories: list[str] = Field(
        description="High-level categories of startup expenses"
    )
    low_cost_mvp: list[str] = Field(
        description="Ways to build a low-cost MVP"
    )
    revenue_models: list[str] = Field(
        description="Possible revenue models"
    )
    financial_constraints: list[str] = Field(
        description="Important financial constraints"
    )
    recommendations: list[str] = Field(
        description="Practical financial recommendations"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


structured_llm = llm.with_structured_output(FinancialAnalysis)


def finance_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}
    market_analysis = state.get("market_analysis") or {}

    prompt = f"""
You are the Finance Agent in an AI Personalized Startup Mentor.

Analyze the financial feasibility of the startup.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Market Agent Analysis:
{market_analysis}

Consider:

1. Financial practicality
2. Founder budget
3. High-level expense categories
4. Low-cost MVP approach
5. Possible revenue models
6. Financial constraints
7. Practical recommendations

Personalize the analysis using the founder's:
- Budget
- Skills
- Experience
- Goals

The founder may be a student with a limited budget.

Do not invent precise financial facts, costs, or market statistics.
Do not present guesses as real financial data.

Keep the analysis practical and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "financial_analysis": result.model_dump()
    }