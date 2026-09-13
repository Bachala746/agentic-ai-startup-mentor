from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
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
    return {
        "message": f"Startup idea received successfully for {request.mentor}!"
    }