import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.graph import startup_graph


load_dotenv()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartupRequest(BaseModel):
    startupIdea: str
    founderProfile: dict | None = None
    mentor: str


@app.get("/")
def home():
    return {
        "message": "Agentic AI Startup Mentor Backend is running!"
    }


@app.post("/startup-plan")
def startup_plan(request: StartupRequest):

    initial_state = {
        "startup_idea": request.startupIdea,
        "founder_profile": request.founderProfile,
        "mentor": request.mentor,
    }

    print("Starting LangGraph workflow...")

    result = startup_graph.invoke(initial_state)

    print("LangGraph workflow completed.")

    decision = result.get("decision_analysis", {})

    return {
        "message": decision.get(
            "overall_assessment",
            result.get("final_recommendation", "No recommendation generated.")
        ),
        "market_analysis": result.get("market_analysis", {}),
        "financial_analysis": result.get("financial_analysis", {}),
        "risk_analysis": result.get("risk_analysis", {}),
        "roadmap": result.get("roadmap", []),
    }