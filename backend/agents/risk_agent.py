import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def risk_agent(startup_idea, founder_profile=None):
    prompt = f"""
You are the Risk Analysis Agent of an AI Startup Mentor.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Analyze the major risks and challenges of this startup.

Provide:
1. Business risks
2. Market risks
3. Financial risks
4. Technical risks
5. Customer/adoption risks
6. Simple ways to reduce these risks

Keep the analysis practical and easy to understand.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text