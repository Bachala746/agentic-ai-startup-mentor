from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Agentic AI Startup Mentor Backend is running!"
    }