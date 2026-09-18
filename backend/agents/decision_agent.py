import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def decision_agent(startup_idea, market_analysis, finance_analysis, risk_analysis):
    prompt = f"""
You are the Decision Agent of an AI Startup Mentor.

Startup Idea:
{startup_idea}

Market Agent Analysis:
{market_analysis}

Finance Agent Analysis:
{finance_analysis}

Risk Agent Analysis:
{risk_analysis}

Combine the above analyses and create a final startup guidance.

Provide:
1. Overall idea assessment
2. Key opportunity
3. Main financial consideration
4. Main risks
5. Recommended next steps
6. Simple 30-day startup roadmap

Keep the response practical, clear, and easy to understand.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text