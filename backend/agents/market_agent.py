import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def market_agent(startup_idea):
    prompt = f"""
You are the Market Research Agent of an AI Startup Mentor.

Analyze this startup idea:

{startup_idea}

Provide a simple market analysis with:

1. Target customers
2. Market demand
3. Customer problem
4. Market opportunity
5. Main competitors or similar solutions
6. Market challenges

Give practical and easy-to-understand points.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text