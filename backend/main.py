import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

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

class ChatRequest(BaseModel):
    message: str
    startupIdea: str = ""
    mentor: str
    founderProfile: dict | None = None

class SavePlanRequest(BaseModel):
    userEmail: str
    startupIdea: str
    mentor: str
    marketAnalysis: dict
    financialAnalysis: dict
    riskAnalysis: dict
    roadmap: list[str]
    roadmapProgress: list[int] = []
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
            roadmap_progress,
            final_decision
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.userEmail,
            request.startupIdea,
            request.mentor,
            json.dumps(request.marketAnalysis),
            json.dumps(request.financialAnalysis),
            json.dumps(request.riskAnalysis),
            json.dumps(request.roadmap),
            json.dumps(request.roadmapProgress),
            request.finalDecision,
        ),
    )

    plan_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "message": "Startup plan saved successfully!",
        "planId": plan_id
    }
class RoadmapProgressRequest(BaseModel):
    planId: int
    completedSteps: list[int]


@app.put("/update-roadmap-progress")
def update_roadmap_progress(request: RoadmapProgressRequest):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE startup_plans
        SET roadmap_progress = ?
        WHERE id = ?
        """,
        (
            json.dumps(request.completedSteps),
            request.planId,
        ),
    )

    connection.commit()
    connection.close()

    return {"message": "Roadmap progress updated successfully!"}
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

@app.post("/mentor-chat")
def mentor_chat(request: ChatRequest):
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite"
        )

        profile = request.founderProfile or {}

        prompt = f"""
You are an AI startup mentor.

USER PROFILE:
Name: {profile.get("fullName", "Not provided")}
Skills: {profile.get("skills", "Not provided")}
Interests: {profile.get("interests", "Not provided")}
Experience: {profile.get("experience", "Not provided")}
Budget: {profile.get("budget", "Not provided")}
Goals: {profile.get("goals", "Not provided")}

STARTUP IDEA:
{request.startupIdea or "No startup idea provided"}

SELECTED MENTOR:
{request.mentor}

USER QUESTION:
{request.message}

Give a practical, simple, and personalized answer.

Use the user's profile when relevant:
- Consider their skills when suggesting technical approaches.
- Consider their interests when suggesting opportunities.
- Consider their experience when giving recommendations.
- Consider their budget when suggesting solutions.
- Consider their goals when suggesting next steps.
- If no startup idea is provided, use the user's profile to provide relevant startup guidance.
- Do not invent profile information.

IMPORTANT:
- Use clear headings for different topics.
- Use bullet points for lists.
- Use numbered points for steps.
- Use **bold text** to highlight important words.
- Keep each point short and easy to understand.
- Do not write one large continuous paragraph.
- Use Markdown formatting.
- Give practical examples when useful.
- Do not use horizontal lines or "---".
- Keep the response visually clean and professional.
- Focus on helping the user build and improve their startup.
"""

        response = model.invoke(prompt)

        if isinstance(response.content, str):
            reply = response.content
        elif isinstance(response.content, list):
            reply = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in response.content
            )
        else:
            reply = str(response.content)

        return {
            "reply": reply
        }

    except Exception as error:
        print("Mentor chat error:", error)
        return {
            "reply": "Sorry, I could not generate a response right now."
        }