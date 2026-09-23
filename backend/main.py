import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.graph import startup_graph
from database import create_tables
from database import get_connection


load_dotenv()

create_tables()

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
    
class SavePlanRequest(BaseModel):
    userEmail: str
    startupIdea: str
    mentor: str
    marketAnalysis: dict
    financialAnalysis: dict
    riskAnalysis: dict
    roadmap: list[str]
    finalDecision: str


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
@app.post("/save-plan")
def save_plan(request: SavePlanRequest):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO startup_plans (
            user_email,
            startup_idea,
            mentor,
            market_analysis,
            financial_analysis,
            risk_analysis,
            roadmap,
            final_decision
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.userEmail,
            request.startupIdea,
            request.mentor,
            json.dumps(request.marketAnalysis),
            json.dumps(request.financialAnalysis),
            json.dumps(request.riskAnalysis),
            json.dumps(request.roadmap),
            request.finalDecision,
        ),
    )

    connection.commit()
    connection.close()

    return {"message": "Startup plan saved successfully!"}
@app.get("/saved-plans")
def get_saved_plans(user_email: str = ""):
    connection = get_connection()
    cursor = connection.cursor()

    if user_email:
        cursor.execute(
            """
            SELECT id, user_email, startup_idea, mentor,
                   market_analysis, financial_analysis,
                   risk_analysis, roadmap, final_decision,
                   created_at
            FROM startup_plans
            WHERE user_email = ?
            ORDER BY created_at DESC
            """,
            (user_email,),
        )
    else:
        cursor.execute(
            """
            SELECT id, user_email, startup_idea, mentor,
                   market_analysis, financial_analysis,
                   risk_analysis, roadmap, final_decision,
                   created_at
            FROM startup_plans
            ORDER BY created_at DESC
            """
        )

    rows = cursor.fetchall()
    connection.close()

    plans = []

    for row in rows:
        plans.append({
            "id": row[0],
            "user_email": row[1],
            "startup_idea": row[2],
            "mentor": row[3],
            "market_analysis": json.loads(row[4]),
            "financial_analysis": json.loads(row[5]),
            "risk_analysis": json.loads(row[6]),
            "roadmap": json.loads(row[7]),
            "final_decision": row[8],
            "created_at": row[9],
        })

    return {"plans": plans}