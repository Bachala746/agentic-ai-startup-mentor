import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def finance_agent(startup_idea, founder_profile=None):
    prompt = f"""
You are the Finance Agent of an AI Startup Mentor.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Analyze the financial feasibility of this startup.

Provide:
1. Estimated starting costs
2. Budget feasibility
3. Possible revenue models
4. Major expenses
5. Basic financial challenges
6. Simple financial suggestions

Keep the analysis practical and easy to understand.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text