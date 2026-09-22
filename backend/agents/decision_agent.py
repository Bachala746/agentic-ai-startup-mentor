import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import StartupState


load_dotenv()


class DecisionAnalysis(BaseModel):
    overall_assessment: str = Field(
        description="Overall personalized assessment of the startup idea"
    )
    key_opportunities: list[str] = Field(
        description="Most important opportunities"
    )
    main_considerations: list[str] = Field(
        description="Most important financial, market, or implementation considerations"
    )
    main_risks: list[str] = Field(
        description="Most important risks"
    )
    mvp_direction: list[str] = Field(
        description="Practical direction for building the MVP"
    )
    next_actions: list[str] = Field(
        description="Most important immediate actions for the founder"
    )
    roadmap: list[str] = Field(
        description="Step-by-step startup roadmap"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


structured_llm = llm.with_structured_output(DecisionAnalysis)


def decision_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}
    market_analysis = state.get("market_analysis") or {}
    financial_analysis = state.get("financial_analysis") or {}
    risk_analysis = state.get("risk_analysis") or {}

    prompt = f"""
You are the Decision Agent in an AI Personalized Startup Mentor.

Your job is to synthesize the outputs of the Market, Finance, and Risk Agents
and provide personalized startup guidance.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Market Agent Analysis:
{market_analysis}

Finance Agent Analysis:
{financial_analysis}

Risk Agent Analysis:
{risk_analysis}

Create a personalized decision and action plan.

Consider the founder's:
- Skills
- Interests
- Experience
- Budget
- Goals

Provide:

1. Overall assessment
2. Key opportunities
3. Main considerations
4. Main risks
5. MVP direction
6. Immediate next actions
7. Step-by-step startup roadmap

Do not simply concatenate the three agent outputs.
Synthesize them into practical guidance.

Do not invent precise market or financial facts.
Keep the recommendations realistic and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "final_recommendation": result.overall_assessment,
        "roadmap": result.roadmap,
        "decision_analysis": result.model_dump(),
    }