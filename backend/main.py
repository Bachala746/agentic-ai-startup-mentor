import os
import json

from fastapi import FastAPI, HTTPException
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


class IdeaOverviewRequest(BaseModel):
    startupIdea: str


class IdeaOverview(BaseModel):
    title: str
    description: str
    problem: list[str]
    target_users: list[str]
    key_features: list[str]
    how_it_works: list[str]
    first_steps: list[str]
    opportunity: str
    challenges: list[str]


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


class RoadmapProgressRequest(BaseModel):
    planId: int
    completedSteps: list[int]


@app.get("/")
def home():
    return {
        "message": "Agentic AI Startup Mentor Backend is running!"
    }


@app.post("/idea-overview")
def idea_overview(request: IdeaOverviewRequest):
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite"
        )

        prompt = f"""
You are an AI startup mentor.

Analyze this startup idea:

{request.startupIdea}

Give a simple startup idea overview.

Return ONLY valid JSON with exactly these fields:

{{
    "title": "short title",
    "description": "simple description",
    "problem": ["problem 1", "problem 2"],
    "target_users": ["user 1", "user 2"],
    "key_features": ["feature 1", "feature 2", "feature 3"],
    "how_it_works": ["step 1", "step 2", "step 3"],
    "first_steps": ["step 1", "step 2", "step 3"],
    "opportunity": "simple explanation of the opportunity",
    "challenges": ["challenge 1", "challenge 2", "challenge 3"]
}}

Do not add any other fields.
"""

        response = model.invoke(prompt)

        content = response.content

        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                if isinstance(item, dict)
                else str(item)
                for item in content
            )

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]

        if content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    except Exception as error:
        error_text = str(error)

        print("Idea overview error:", error_text)

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_type": "AI_SERVICE_BUSY",
                    "message": (
                        "The AI service is temporarily busy. "
                        "Please try again in a few moments."
                    ),
                },
            )

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise HTTPException(
                status_code=429,
                detail={
                    "error_type": "AI_REQUEST_LIMIT",
                    "message": (
                        "The AI request limit has been reached. "
                        "Please try again later."
                    ),
                },
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "AI_GENERATION_ERROR",
                "message": "Unable to generate startup overview.",
            },
        )


@app.post("/startup-plan")
def startup_plan(request: StartupRequest):
    try:
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
                result.get(
                    "final_recommendation",
                    "No recommendation generated.",
                ),
            ),
            "market_analysis": result.get(
                "market_analysis",
                {},
            ),
            "financial_analysis": result.get(
                "financial_analysis",
                {},
            ),
            "risk_analysis": result.get(
                "risk_analysis",
                {},
            ),
            "roadmap": result.get(
                "roadmap",
                [],
            ),
            "web_sources": result.get(
                "web_sources",
                [],
            ),
        }

    except Exception as error:
        print("Startup plan error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to generate startup plan.",
        )


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
        "planId": plan_id,
    }


@app.delete("/saved-plans/{plan_id}")
def delete_saved_plan(plan_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM startup_plans WHERE id = ?",
        (plan_id,),
    )

    connection.commit()
    connection.close()

    return {
        "message": "Startup plan deleted successfully!"
    }


@app.put("/update-roadmap-progress")
def update_roadmap_progress(
    request: RoadmapProgressRequest
):
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

    return {
        "message": "Roadmap progress updated successfully!"
    }


@app.get("/saved-plans")
def get_saved_plans(user_email: str = ""):
    connection = get_connection()
    cursor = connection.cursor()

    if user_email:
        cursor.execute(
            """
            SELECT
                id,
                user_email,
                startup_idea,
                mentor,
                market_analysis,
                financial_analysis,
                risk_analysis,
                roadmap,
                roadmap_progress,
                final_decision,
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
            SELECT
                id,
                user_email,
                startup_idea,
                mentor,
                market_analysis,
                financial_analysis,
                risk_analysis,
                roadmap,
                roadmap_progress,
                final_decision,
                created_at
            FROM startup_plans
            ORDER BY created_at DESC
            """
        )

    rows = cursor.fetchall()
    connection.close()

    plans = []

    for row in rows:
        plans.append(
            {
                "id": row[0],
                "user_email": row[1],
                "startup_idea": row[2],
                "mentor": row[3],
                "market_analysis": json.loads(row[4]),
                "financial_analysis": json.loads(row[5]),
                "risk_analysis": json.loads(row[6]),
                "roadmap": json.loads(row[7]),
                "roadmap_progress": json.loads(row[8]),
                "final_decision": row[9],
                "created_at": row[10],
            }
        )

    return {
        "plans": plans
    }


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

Name:
{profile.get("fullName", "Not provided")}

Skills:
{profile.get("skills", "Not provided")}

Interests:
{profile.get("interests", "Not provided")}

Experience:
{profile.get("experience", "Not provided")}

Budget:
{profile.get("budget", "Not provided")}

Goals:
{profile.get("goals", "Not provided")}

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
- If no startup idea is provided, use the user's profile.
- Do not invent profile information.

IMPORTANT:

- Use clear headings.
- Use bullet points for lists.
- Use numbered points for steps.
- Use Markdown formatting.
- Keep each point short.
- Do not write one large continuous paragraph.
- Do not use horizontal lines.
- Keep the response professional.
"""

        response = model.invoke(prompt)

        if isinstance(response.content, str):
            reply = response.content

        elif isinstance(response.content, list):
            reply = "".join(
                item.get("text", "")
                if isinstance(item, dict)
                else str(item)
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
            "reply": (
                "Sorry, I could not generate a response "
                "right now."
            )
        }