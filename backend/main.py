import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

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

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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

    prompt = f"""
You are an AI Startup Mentor.

Startup Idea:
{request.startupIdea}

Founder Profile:
{request.founderProfile}

Selected Mentor:
{request.mentor}

Give simple and practical startup guidance.

Include:
1. Idea validation
2. Target customers
3. Revenue model
4. Main risks
5. Next steps
"""

    print("Sending request to Gemini...")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    print("Gemini response received.")

    return {
        "message": response.text
    }