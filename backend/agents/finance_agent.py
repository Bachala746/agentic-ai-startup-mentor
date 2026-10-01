import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS

from .state import StartupState


load_dotenv()


class FinancialAnalysis(BaseModel):
    financial_practicality: str = Field(
        description="Overall financial practicality of the startup"
    )
    expense_categories: list[str] = Field(
        description="High-level categories of startup expenses"
    )
    low_cost_mvp: list[str] = Field(
        description="Ways to build a low-cost MVP"
    )
    revenue_models: list[str] = Field(
        description="Possible revenue models"
    )
    financial_constraints: list[str] = Field(
        description="Important financial constraints"
    )
    recommendations: list[str] = Field(
        description="Practical financial recommendations"
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

structured_llm = llm.with_structured_output(FinancialAnalysis)


def finance_agent(state: StartupState):
    startup_idea = state["startup_idea"]
    founder_profile = state.get("founder_profile") or {}
    market_analysis = state.get("market_analysis") or {}

    # -----------------------------------------
    # Dynamic Finance Web Search
    # -----------------------------------------

    queries = [
        {
            "category": "Financial Costs",
            "queries": [
                f"{startup_idea} startup costs",
                f"{startup_idea} business expenses",
            ],
        },
        {
            "category": "Pricing and Revenue",
            "queries": [
                f"{startup_idea} pricing revenue",
                f"{startup_idea} business model",
            ],
        },
        {
            "category": "Funding and Investment",
            "queries": [
                f"{startup_idea} startup funding",
                f"{startup_idea} investment",
            ],
        },
    ]

    web_results = []

    for search in queries:
        category = search["category"]

        for search in queries:
            category = search["category"]

            for query in search["queries"]:
                try:
                    results = DDGS().text(
                        query,
                        max_results=5
                    )

                    results = list(results)

                    # Fallback search if no results
                    if not results:
                        simple_query = f"{startup_idea} finance"

                        results = list(
                            DDGS().text(
                                simple_query,
                                max_results=5
                            )
                        )

                    for result in results:
                        web_results.append(
                            {
                                "category": category,
                                "title": result.get("title", ""),
                                "url": result.get("href", ""),
                                "snippet": result.get("body", ""),
                            }
                        )

                except Exception as error:
                    print(
                        f"Finance web search failed for '{query}': {error}"
                    )
    # Remove duplicate URLs
    unique_results = []
    seen_urls = set()

    for result in web_results:
        url = result.get("url", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    # Keep maximum 15 sources
    web_results = unique_results[:15]
    print(f"Finance web results: {len(web_results)}")

    # -----------------------------------------
    # Finance AI Analysis
    # -----------------------------------------

    prompt = f"""
You are the Finance Agent in an AI Personalized Startup Mentor.

Analyze the financial feasibility of the startup using the startup
information and the current web research provided below.

Startup Idea:
{startup_idea}

Founder Profile:
{founder_profile}

Market Agent Analysis:
{market_analysis}

Current Financial Web Research:
{web_results}

Consider:

1. Financial practicality
2. Founder budget
3. High-level expense categories
4. Low-cost MVP approach
5. Possible revenue models
6. Financial constraints
7. Practical recommendations

Use the web research when it is relevant to the startup.

Personalize the analysis using the founder's:
- Budget
- Skills
- Experience
- Goals

The founder may be a student with a limited budget.

Important rules:

- Do not invent precise financial facts, costs, prices, funding amounts,
  or market statistics.
- Do not present guesses as real financial data.
- Use the provided web research as supporting information.
- If the web research does not provide enough evidence, give a
  general practical analysis instead of inventing facts.
- Keep the analysis practical and easy to understand.
"""

    result = structured_llm.invoke(prompt)

    return {
        "financial_analysis": result.model_dump(),
        "financial_web_sources": web_results,
    }